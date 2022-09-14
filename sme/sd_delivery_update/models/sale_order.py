# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sd_amount_delivery = fields.Monetary(
        compute='_compute_sd_amount_delivery',
        string='Shipping Cost', store=True, tracking=True)

    @api.depends('order_line.price_unit', 'order_line.tax_id', 'order_line.discount', 'order_line.product_uom_qty')
    def _compute_sd_amount_delivery(self):
        for order in self:
            if self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                order.sd_amount_delivery = sum(order.order_line.filtered('is_delivery').mapped('price_subtotal'))
            else:
                order.sd_amount_delivery = sum(order.order_line.filtered('is_delivery').mapped('price_total'))
