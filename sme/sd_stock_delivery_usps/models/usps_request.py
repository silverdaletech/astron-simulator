from odoo.addons.delivery_usps.models.usps_request import USPSRequest, split_zip

class USPSRequest(USPSRequest):

    def _usps_request_data(self,  carrier, order):
        if order._name != 'stock.picking':
            return super(USPSRequest, self)._usps_request_data(carrier, order)
        currency = carrier.env['res.currency'].search([('name', '=', 'USD')], limit=1)  # USPS Works in USDollars
        order._compute_shipping_weight()
        tot_weight = order.shipping_weight
        total_weight = carrier._usps_convert_weight(tot_weight)
        # total_value = sum([(line.price_unit * line.product_uom_qty) for line in order.order_line.filtered(lambda line: not line.is_delivery and not line.display_type)]) or 0.0

        # if order.currency_id.name == currency.name:
        #     price = total_value
        # else:
        #     quote_currency = order.currency_id
        #     price = quote_currency._convert(
        #         total_value, currency, order.company_id, order.date_order or fields.Date.today())
        id =  carrier.sudo().usps_username
        if order.is_partner_shipping_account:
            id =  order.partner_id.sudo().usps_username
        if not id:
            id = '0'
        rate_detail = {
            'api': 'RateV4' if carrier.usps_delivery_nature == 'domestic' else 'IntlRateV2',
            'ID':id,
            'revision': "2",
            'package_id': '%s%d' % ("PKG", order.id),
            'ZipOrigination': split_zip(order.picking_type_id.warehouse_id.partner_id.zip)[0],
            'ZipDestination': split_zip(order.partner_id.zip)[0],
            'FirstClassMailType': carrier.usps_first_class_mail_type,
            'Pounds': total_weight['pound'],
            'Ounces': total_weight['ounce'],
            'Size': carrier.usps_size_container,
            'Service': carrier.usps_service,
            'Container': carrier.usps_container,
            'DomesticRegularontainer': carrier.usps_domestic_regular_container,
            'InternationalRegularContainer': carrier.usps_international_regular_container,
            'MailType': carrier.usps_mail_type,
            'Machinable': str(carrier.usps_machinable),
            'ValueOfContents': 0,
            'Country': order.partner_id.country_id.name,
            'Width': carrier.usps_custom_container_width,
            'Height': carrier.usps_custom_container_height,
            'Length': carrier.usps_custom_container_length,
            'Girth': carrier.usps_custom_container_girth,
        }

        # # Shipping to Canada requires additional information
        if order.partner_id.country_id.code == "CA":
            rate_detail.update(OriginZip=order.picking_type_id.warehouse_id.partner_id.zip)

        return rate_detail

    def _usps_shipping_data(self, picking, is_return=False):
        shipping_detail = super(USPSRequest, self)._usps_shipping_data(picking, is_return)
        carrier = picking.carrier_id
        id =  carrier.sudo().usps_username
        if picking.is_partner_shipping_account:
            id =  picking.partner_id.sudo().usps_username
        if not id:
            id = '0'
        shipping_detail.update({
            'ID':id,
        })
        return shipping_detail

    def _usps_cancel_shipping_data(self, picking):
        shipping_detail = super(USPSRequest, self)._usps_cancel_shipping_data(picking)
        carrier = picking.carrier_id
        id =  carrier.sudo().usps_username
        if picking.is_partner_shipping_account:
            id =  picking.partner_id.sudo().usps_username
        if not id:
            id = '0'
        shipping_detail.update({
            'ID':id,
        })
        return shipping_detail
