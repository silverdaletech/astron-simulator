# -*- coding: utf-8 -*-
import logging
import time

from odoo import api, models, fields, _, tools
from odoo.exceptions import UserError
from odoo.tools import pdf
from odoo.addons.delivery_fedex.models.delivery_fedex import _convert_curr_iso_fdx, _convert_curr_fdx_iso
from .fedex_request import FedexRequest

_logger = logging.getLogger(__name__)


class ProviderFedex(models.Model):
    _inherit = 'delivery.carrier'

    ##############################################
    #Send shippment to fedex inherited from fedex
    ##############################################
    def fedex_send_shipping(self, pickings):
        """
            Override fedex base module:
            Use fedex account credentials from company or customer based on wizard selection.
            Configuration use from main fedex record.
        """
        res = []

        for picking in pickings:

            srm = FedexRequest(self.log_xml, request_type="shipping", prod_environment=self.prod_environment)
            superself = self.sudo()
            
            fedex_developer_key = superself.fedex_developer_key
            fedex_developer_password = superself.fedex_developer_password
            fedex_account_number = superself.fedex_account_number
            fedex_meter_number = superself.fedex_meter_number

            srm.web_authentication_detail(fedex_developer_key, fedex_developer_password)
            srm.client_detail(fedex_account_number, fedex_meter_number)

            srm.transaction_detail(picking.id)

            package_type = picking.package_ids and picking.package_ids[0].package_type_id.shipper_package_code or self.fedex_default_package_type_id.shipper_package_code
            srm.shipment_request(self.fedex_droppoff_type, self.fedex_service_type, package_type, self.fedex_weight_unit, self.fedex_saturday_delivery)
            srm.set_currency(_convert_curr_iso_fdx(picking.company_id.currency_id.name))
            srm.set_shipper(picking.company_id.partner_id, picking.picking_type_id.warehouse_id.partner_id)
            srm.set_recipient(picking.partner_id)

            if pickings.is_partner_shipping_account and picking.sale_id:
                customer_fedex_account_number = picking.sale_id.partner_id.with_company(picking.company_id).fedex_account_number
                srm.shipping_charges_payment_option(customer_fedex_account_number, 'RECIPIENT')
                if not customer_fedex_account_number:
                    raise UserError("Please set Fedex Account number on customer.")
            else:
                srm.shipping_charges_payment_option(fedex_account_number, 'SENDER')

            srm.shipment_label('COMMON2D', self.fedex_label_file_type, self.fedex_label_stock_type, 'TOP_EDGE_OF_TEXT_FIRST', 'SHIPPING_LABEL_FIRST')

            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.company
            order_currency = picking.sale_id.currency_id or picking.company_id.currency_id

            net_weight = self._fedex_convert_weight(picking.shipping_weight, self.fedex_weight_unit)

            # Commodities for customs declaration (international shipping)
            if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_PRIORITY'] or (picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN'):

                commodity_currency = order_currency
                total_commodities_amount = 0.0
                commodity_country_of_manufacture = picking.picking_type_id.warehouse_id.partner_id.country_id.code

                for operation in picking.move_line_ids:
                    total_commodities_amount += operation.sale_price
                    commodity_description = operation.product_id.name
                    commodity_number_of_piece = '1'
                    commodity_weight_units = self.fedex_weight_unit
                    commodity_weight_value = self._fedex_convert_weight(operation.product_id.weight * operation.qty_done, self.fedex_weight_unit)
                    commodity_quantity = operation.qty_done
                    commodity_quantity_units = 'EA'
                    commodity_harmonized_code = operation.product_id.hs_code or ''
                    commodity_amount = round(operation.sale_price/commodity_quantity, 2) if commodity_quantity else operation.sale_price

                    srm.commodities(_convert_curr_iso_fdx(commodity_currency.name), commodity_amount, commodity_number_of_piece, commodity_weight_units, commodity_weight_value, commodity_description, commodity_country_of_manufacture, commodity_quantity, commodity_quantity_units, commodity_harmonized_code)
                srm.customs_value(_convert_curr_iso_fdx(commodity_currency.name), total_commodities_amount, "NON_DOCUMENTS")
                # srm.duties_payment(picking.picking_type_id.warehouse_id.partner_id, fedex_account_number, superself.fedex_duty_payment)
                if pickings.is_partner_shipping_account and picking.sale_id:
                    customer_fedex_account_number = picking.sale_id.partner_id.with_company(picking.company_id).fedex_account_number
                    if not customer_fedex_account_number:
                        raise UserError("Please set Fedex Account number on customer.")
                    srm.duties_payment_option(picking.sale_id.partner_id.with_company(picking.company_id), customer_fedex_account_number, 'RECIPIENT')
                else:
                    srm.duties_payment_option(picking.picking_type_id.warehouse_id.partner_id, fedex_account_number, 'SENDER')
                
                send_etd = superself.env['ir.config_parameter'].get_param("delivery_fedex.send_etd")
                srm.commercial_invoice(self.fedex_document_stock_type, send_etd)

            package_count = len(picking.package_ids) or 1

            # For india picking courier is not accepted without this details in label.
            po_number = order.display_name or False
            dept_number = False
            if picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN':
                po_number = 'B2B' if picking.partner_id.commercial_partner_id.is_company else 'B2C'
                dept_number = 'BILL D/T: SENDER'

            # TODO RIM master: factorize the following crap

            ################
            # Multipackage #
            ################
            if package_count > 1:

                # Note: Fedex has a complex multi-piece shipping interface
                # - Each package has to be sent in a separate request
                # - First package is called "master" package and holds shipping-
                #   related information, including addresses, customs...
                # - Last package responses contains shipping price and code
                # - If a problem happens with a package, every previous package
                #   of the shipping has to be cancelled separately
                # (Why doing it in a simple way when the complex way exists??)

                master_tracking_id = False
                package_labels = []
                carrier_tracking_ref = ""

                for sequence, package in enumerate(picking.package_ids, start=1):

                    package_weight = self._fedex_convert_weight(package.shipping_weight, self.fedex_weight_unit)
                    package_type = package.package_type_id
                    srm._add_package(
                        package_weight,
                        package_code=package_type.shipper_package_code,
                        package_height=package_type.height,
                        package_width=package_type.width,
                        package_length=package_type.packaging_length,
                        sequence_number=sequence,
                        po_number=po_number,
                        dept_number=dept_number,
                        reference=picking.display_name,
                    )
                    srm.set_master_package(net_weight, package_count, master_tracking_id=master_tracking_id)
                    request = srm.process_shipment()
                    package_name = package.name or sequence

                    warnings = request.get('warnings_message')
                    if warnings:
                        _logger.info(warnings)

                    # First package
                    if sequence == 1:
                        if not request.get('errors_message'):
                            master_tracking_id = request['master_tracking_id']
                            package_labels.append((package_name, srm.get_label()))
                            carrier_tracking_ref = request['tracking_number']
                        else:
                            raise UserError(request['errors_message'])

                    # Intermediary packages
                    elif sequence > 1 and sequence < package_count:
                        if not request.get('errors_message'):
                            package_labels.append((package_name, srm.get_label()))
                            carrier_tracking_ref = carrier_tracking_ref + "," + request['tracking_number']
                        else:
                            raise UserError(request['errors_message'])

                    # Last package
                    elif sequence == package_count:
                        # recuperer le label pdf
                        if not request.get('errors_message'):
                            package_labels.append((package_name, srm.get_label()))

                            carrier_price = self._get_request_price(request['price'], order, order_currency)

                            carrier_tracking_ref = carrier_tracking_ref + "," + request['tracking_number']

                            logmessage = _("Shipment created into Fedex<br/>"
                                           "<b>Tracking Numbers:</b> %s<br/>"
                                           "<b>Packages:</b> %s") % (carrier_tracking_ref, ','.join([pl[0] for pl in package_labels]))
                            if self.fedex_label_file_type != 'PDF':
                                attachments = [('LabelFedex-%s.%s' % (pl[0], self.fedex_label_file_type), pl[1]) for pl in package_labels]
                            if self.fedex_label_file_type == 'PDF':
                                attachments = [('LabelFedex.pdf', pdf.merge_pdf([pl[1] for pl in package_labels]))]
                            picking.message_post(body=logmessage, attachments=attachments)
                            shipping_data = {'exact_price': carrier_price,
                                             'tracking_number': carrier_tracking_ref}
                            res = res + [shipping_data]
                        else:
                            raise UserError(request['errors_message'])

            # TODO RIM handle if a package is not accepted (others should be deleted)

            ###############
            # One package #
            ###############
            elif package_count == 1:
                package_type = picking.package_ids[:1].package_type_id or picking.carrier_id.fedex_default_package_type_id
                srm._add_package(
                    net_weight,
                    package_code=package_type.shipper_package_code,
                    package_height=package_type.height,
                    package_width=package_type.width,
                    package_length=package_type.packaging_length,
                    po_number=po_number,
                    dept_number=dept_number,
                    reference=picking.display_name,
                )
                srm.set_master_package(net_weight, 1)

                # Ask the shipping to fedex
                request = srm.process_shipment()

                warnings = request.get('warnings_message')
                if warnings:
                    _logger.info(warnings)

                if not request.get('errors_message'):

                    if _convert_curr_iso_fdx(order_currency.name) in request['price']:
                        carrier_price = request['price'][_convert_curr_iso_fdx(order_currency.name)]
                    else:
                        _logger.info("Preferred currency has not been found in FedEx response")
                        company_currency = picking.company_id.currency_id
                        if _convert_curr_iso_fdx(company_currency.name) in request['price']:
                            amount = request['price'][_convert_curr_iso_fdx(company_currency.name)]
                            carrier_price = company_currency._convert(
                                amount, order_currency, company, fields.Date.today())
                        else:
                            amount = request['price']['USD']
                            carrier_price = company_currency._convert(
                                amount, order_currency, company, fields.Date.today())

                    carrier_tracking_ref = request['tracking_number']
                    logmessage = (_("Shipment created into Fedex <br/> <b>Tracking Number : </b>%s") % (carrier_tracking_ref))

                    fedex_labels = [('LabelFedex-%s-%s.%s' % (carrier_tracking_ref, index, self.fedex_label_file_type), label)
                                    for index, label in enumerate(srm._get_labels(self.fedex_label_file_type))]
                    
                    # Dont post tracking number in all related delivery orders
                    # Removed loged note in related deliveries
                    # if picking.sale_id:
                    #     for pick in picking.sale_id.picking_ids:
                    #         pick.message_post(body=logmessage, attachments=fedex_labels)
                    # else:
                    picking.message_post(body=logmessage, attachments=fedex_labels)
                    shipping_data = {'exact_price': carrier_price,
                                     'tracking_number': carrier_tracking_ref}
                    res = res + [shipping_data]
                else:
                    raise UserError(request['errors_message'])

            ##############
            # No package #
            ##############
            else:
                raise UserError(_('No packages for this picking'))
            if self.return_label_on_delivery:
                self.get_return_label(picking, tracking_number=request['tracking_number'], origin_date=request['date'])
            commercial_invoice = srm.get_document()
            if commercial_invoice:
                fedex_documents = [('DocumentFedex.pdf', commercial_invoice)]
                picking.message_post(body='Fedex Documents', attachments=fedex_documents)
        return res

    #####################################
    #Get shippment rate from fedex
    #####################################
    def fedex_picking_rate_shipment(self, delivery):
        """
            call from picking_rate_shipment.
            Get shipmnet rate on delivery form.
        """
        max_weight = self._fedex_convert_weight(self.fedex_default_package_type_id.max_weight, self.fedex_weight_unit)
        price = 0.0

        is_india = delivery.partner_id.country_id.code == 'IN' and delivery.company_id.partner_id.country_id.code == 'IN'

        # Compute delivery weight
        delivery._compute_shipping_weight()

        weight_value = self._fedex_convert_weight(delivery.shipping_weight, self.fedex_weight_unit)

        # Some users may want to ship very lightweight items; in order to give them a rating, we round the
        # converted weight of the shipping to the smallest value accepted by FedEx: 0.01 kg or lb.
        # (in the case where the weight is actually 0.0 because weights are not set, don't do this)
        if weight_value > 0.0:
            weight_value = max(weight_value, 0.01)

        order_currency = delivery.company_id.currency_id
        superself = self.sudo()

        # Authentication stuff
        fedex_developer_key = superself.fedex_developer_key
        fedex_developer_password = superself.fedex_developer_password
        fedex_account_number = superself.fedex_account_number
        fedex_meter_number = superself.fedex_meter_number

        # Use Customer account for fexed 
        if delivery.is_partner_shipping_account:
            partner = delivery.partner_id
            fedex_developer_key = partner.fedex_developer_key
            fedex_developer_password = partner.fedex_developer_password
            fedex_account_number = partner.fedex_account_number
            fedex_meter_number = partner.fedex_meter_number

        srm = FedexRequest(self.log_xml, request_type="rating", prod_environment=self.prod_environment)
        srm.web_authentication_detail(fedex_developer_key, fedex_developer_password)
        srm.client_detail(fedex_account_number, fedex_meter_number)

        # Build basic rating request and set addresses
        srm.transaction_detail(delivery.name)
        srm.shipment_request(
            self.fedex_droppoff_type,
            self.fedex_service_type,
            self.fedex_default_package_type_id.shipper_package_code,
            self.fedex_weight_unit,
            self.fedex_saturday_delivery,
        )
        pkg = self.fedex_default_package_type_id

        srm.set_currency(_convert_curr_iso_fdx(order_currency.name))
        srm.set_shipper(delivery.company_id.partner_id, delivery.picking_type_id.warehouse_id.partner_id)
        srm.set_recipient(delivery.partner_id)

        if max_weight and weight_value > max_weight:
            total_package = int(weight_value / max_weight)
            last_package_weight = weight_value % max_weight

            for sequence in range(1, total_package + 1):
                srm.add_package(
                    max_weight,
                    package_code=pkg.shipper_package_code,
                    package_height=pkg.height,
                    package_width=pkg.width,
                    package_length=pkg.packaging_length,
                    sequence_number=sequence,
                    mode='rating',
                )
            if last_package_weight:
                total_package = total_package + 1
                srm.add_package(
                    last_package_weight,
                    package_code=pkg.shipper_package_code,
                    package_height=pkg.height,
                    package_width=pkg.width,
                    package_length=pkg.packaging_length,
                    sequence_number=total_package,
                    mode='rating',
                )
            srm.set_master_package(weight_value, total_package)
        else:
            srm.add_package(
                weight_value,
                package_code=pkg.shipper_package_code,
                package_height=pkg.height,
                package_width=pkg.width,
                package_length=pkg.packaging_length,
                mode='rating',
            )
            srm.set_master_package(weight_value, 1)

        # Commodities for customs declaration (international shipping)
        if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_PRIORITY'] or is_india:
            total_commodities_amount = 0.0
            commodity_country_of_manufacture = delivery.picking_type_id.warehouse_id.partner_id.country_id.code

            for operation in delivery.move_line_ids:
                total_commodities_amount += operation.sale_price
                commodity_description = operation.product_id.name
                commodity_number_of_piece = '1'
                commodity_weight_units = self.fedex_weight_unit
                commodity_weight_value = self._fedex_convert_weight(operation.product_id.weight * operation.qty_done, self.fedex_weight_unit)
                commodity_quantity = operation.qty_done
                commodity_quantity_units = 'EA'
                commodity_harmonized_code = operation.product_id.hs_code or ''
                commodity_amount = round(operation.sale_price/commodity_quantity, 2) if commodity_quantity else operation.sale_price

            srm.customs_value(_convert_curr_iso_fdx(order_currency.name), total_commodities_amount, "NON_DOCUMENTS")
            srm.duties_payment(delivery.picking_type_id.warehouse_id.partner_id, fedex_account_number, superself.fedex_duty_payment)

        request = srm.rate()

        warnings = request.get('warnings_message')
        if warnings:
            _logger.info(warnings)

        if not request.get('errors_message'):
            price = self._get_request_price(request['price'], delivery, order_currency)
        else:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error:\n%s', request['errors_message']),
                    'warning_message': False}

        return {'success': True,
                'price': price,
                'error_message': False,
                'warning_message': _('Warning:\n%s', warnings) if warnings else False}
