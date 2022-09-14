# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    picking_id = fields.Many2one('stock.picking', required=False, ondelete="cascade")
    order_id = fields.Many2one('sale.order', required=False, ondelete="cascade")
    is_partner_shipping_account = fields.Boolean(string="Customer Shipping Account")

    def _get_shipment_rate(self):
        if self.picking_id:
            # vals = self.carrier_id.fedex_picking_rate_shipment(self.picking_id)
            self.picking_id.is_partner_shipping_account = self.is_partner_shipping_account
            vals = self.carrier_id.picking_rate_shipment(self.picking_id)
        else:
            vals = self.carrier_id.rate_shipment(self.order_id)
        
        if not vals:
            return {}
        
        if vals.get('success'):
            self.delivery_message = vals.get('warning_message', False)
            self.delivery_price = vals['price']
            self.display_price = vals['carrier_price']
            return {}
        
        return {'error_message': vals['error_message']}

    def update_price(self):
        vals = self._get_shipment_rate()
        if vals.get('error_message'):
            raise UserError(vals.get('error_message'))
        
        if self.picking_id:
            view_id = self.env.ref('sd_stock_delivery.picking_delivery_carrier_view_form').id
            carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)])
            available_carrier_ids = carriers.available_carriers(self.partner_id) if self.partner_id else carriers
            available_carrier_ids = available_carrier_ids.filtered(lambda l:l.delivery_type in ('fedex', 'ups', 'usps'))
            return {
                'name': _('Add a shipping method'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'choose.delivery.carrier',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'res_id': self.id,
                'target': 'new',
            }

        return {
            'name': _('Add a shipping method'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'res_id': self.id,
            'target': 'new',
        }


    def button_picking_confirm(self):
        picking = self.picking_id 
        if picking:
            picking.carrier_id = self.carrier_id.id
            picking.is_partner_shipping_account = self.is_partner_shipping_account