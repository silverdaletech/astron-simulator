# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_partner_shipping_account = fields.Boolean(string="Customer Shipping Account")

    def send_to_shipper(self):
        self.ensure_one()
        res = self.carrier_id.send_shipping(self)[0]
        if self.carrier_id.free_over and self.sale_id and self.sale_id._compute_amount_total_without_delivery() >= self.carrier_id.amount:
            res['exact_price'] = 0.0
        self.carrier_price = res['exact_price'] * (1.0 + (self.carrier_id.margin / 100.0))
        if res['tracking_number']:
            pickings = self
            pickings.carrier_tracking_ref = res['tracking_number']
        order_currency = self.sale_id.currency_id or self.company_id.currency_id
        msg = _(
            "Shipment sent to carrier %(carrier_name)s for shipping with tracking number %(ref)s<br/>Cost: %(price).2f %(currency)s",
            carrier_name=self.carrier_id.name,
            ref=self.carrier_tracking_ref,
            price=self.carrier_price,
            currency=order_currency.name
        )
        self.message_post(body=msg)
        self._add_delivery_cost_to_so()

    def action_open_delivery_wizard(self):
        view_id = self.env.ref('sd_stock_delivery.picking_delivery_carrier_view_form').id
        carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)])
        available_carrier_ids = carriers.available_carriers(self.partner_id) if self.partner_id else carriers
        sd_stock_delivery = self.env['ir.module.module'].search([('name', '=like', 'sd_stock_delivery_%'),('state', '=', 'installed')])
        delivery = [i.name.split('_')[-1] for i in sd_stock_delivery]
        available_carrier_ids = available_carrier_ids.filtered(lambda l:l.delivery_type in delivery)
        return {
            'name': _('Add a shipping method'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
                'default_carrier_id': self.carrier_id.id,
                'default_available_carrier_ids': available_carrier_ids.ids,
            }
        }

    def _add_delivery_cost_to_so(self):
        self.ensure_one()
        sale_order = self.sale_id
        if sale_order and self.carrier_id.invoice_policy == 'real' and self.carrier_price:
            delivery_lines = sale_order.order_line.filtered(lambda l: l.is_delivery and l.product_id == self.carrier_id.product_id)
            carrier_price = self.carrier_price * (1.0 + (float(self.carrier_id.margin) / 100.0))
            if not delivery_lines:
                sol = sale_order._create_delivery_line(self.carrier_id, carrier_price)
                sol.price_unit = carrier_price
            else:
                
                delivery_line = delivery_lines[0]
                price = delivery_line.price_unit + carrier_price
                delivery_line[0].write({
                    'price_unit': price,
                    # remove the estimated price from the description
                    # 'name': sale_order.carrier_id.with_context(lang=self.partner_id.lang).name,  
                    #  
                    'name': _(' (Estimated Cost: %s )', sale_order._format_currency_amount(price)),   
                })