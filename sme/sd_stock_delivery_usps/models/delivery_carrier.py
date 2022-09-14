# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import time

from odoo import api, models, fields, _, tools
from odoo.exceptions import UserError
from odoo.tools import pdf
from .usps_request import USPSRequest   
_logger = logging.getLogger(__name__)


class ProviderFedex(models.Model):
    _inherit = 'delivery.carrier'

    def usps_picking_rate_shipment(self, order):
        srm = USPSRequest(self.prod_environment, self.log_xml)

        check_result = srm.check_required_value(order.partner_id, self.usps_delivery_nature, order.picking_type_id.warehouse_id.partner_id, picking=order)
        if check_result:
            return {'success': False,
                    'price': 0.0,
                    'error_message': check_result,
                    'warning_message': False}

        quotes = srm.usps_rate_request(order, self)

        if quotes.get('error_message'):
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error:\n%s', quotes['error_message']),
                    'warning_message': False}

        # USPS always returns prices in USD
        currency = order.sale_id.currency_id or order.company_id.currency_id
        if currency == 'USD':
            price = quotes['price']
        else:
            quote_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            price = quote_currency._convert(
              quotes['price'], currency, order.company_id, fields.Date.today())

        return {'success': True,
                'price': price,
                'error_message': False,
                'warning_message': False}

    def usps_send_shipping(self, pickings):
        res = []
        srm = USPSRequest(self.prod_environment, self.log_xml)
        for picking in pickings:
            check_result = srm.check_required_value(picking.partner_id, self.usps_delivery_nature, picking.picking_type_id.warehouse_id.partner_id, picking=picking)
            if check_result:
                raise UserError(check_result)

            booking = srm.usps_request(picking, self.usps_delivery_nature, self.usps_service, is_return=False)

            if booking.get('error_message'):
                raise UserError(booking['error_message'])

            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.company
            currency_order = picking.sale_id.currency_id
            if not currency_order:
                currency_order = picking.company_id.currency_id

            # USPS always returns prices in USD
            if currency_order.name == "USD":
                price = booking['price']
            else:
                quote_currency = self.env['res.currency'].search([('name', '=', "USD")], limit=1)
                price = quote_currency._convert(
                booking['price'], currency_order, company, order.date_order or fields.Date.today())

            carrier_tracking_ref = booking['tracking_number']

            logmessage = (_("Shipment created into USPS <br/> <b>Tracking Number : </b>%s") % (carrier_tracking_ref))
            usps_labels = [('LabelUSPS-%s.%s' % (carrier_tracking_ref, self.usps_label_file_type), booking['label'])]

            #don't post tracking id on related picking order    
            # if picking.sale_id:
            #     for pick in picking.sale_id.picking_ids:
            #         pick.message_post(body=logmessage, attachments=usps_labels)
            # else:
            picking.message_post(body=logmessage, attachments=usps_labels)

            shipping_data = {'exact_price': price,
                             'tracking_number': carrier_tracking_ref}
            res = res + [shipping_data]
            if self.return_label_on_delivery:
                self.get_return_label(picking)
        return res

