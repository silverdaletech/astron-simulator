# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    remaining_amount = fields.Float(string='Additional Shipping Cost', readonly=True, compute="_compute_remaining_amount")
    can_hide = fields.Boolean(compute="_compute_remaining_amount")

    @api.onchange('remaining_amount')
    @api.depends('display_price', 'order_id')
    def _compute_remaining_amount(self):
        """
            Compute remaining delivery amount from sale order
        """
        for rec in self:
            remaining_amount = 0
            if rec.order_id:
                remaining_amount = rec.display_price - rec.order_id.sd_amount_delivery
            rec.remaining_amount = remaining_amount
            carrier_recompute = self.env.context.get('carrier_recompute')
            if rec.remaining_amount == 0 or not carrier_recompute:
                rec.can_hide = True
            else:
                rec.can_hide = False

    def action_add_delivery_product(self):
        """
            Add new delivery order line instead remove old one.
            Add new line because in most of cases user created invoice.
        """
        if self.order_id:
            # additional_price = self.display_price - self.order_id.sd_amount_delivery
            additional_price = self.remaining_amount
            values = {'product_id': self.carrier_id.product_id.id,
                      'order_id': self.order_id.id,
                      'price_unit': additional_price,
                      'is_delivery': True,
                      }
            self.env['sale.order.line'].sudo().create(values)
