# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order', string='Sale order', compute='get_linked_sale_order')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Line ID', tracking=True,
                                   domain="[('order_id','=', sale_order_id), ('product_id', '=', product_id)]")
    manually_added = fields.Boolean(default=False)

    def copy_sale_line_to_backorders(self):
        backorders = self.procurement_group_id.mrp_production_ids.filtered(lambda b: b.state != 'cancel')
        if backorders:
            for order in backorders:
                if order.id != self.id:
                    order.sale_line_id = self.sale_line_id
                    order.manually_added = True
                    self.manually_added = True

    @api.depends('origin')
    def get_linked_sale_order(self):
        for rec in self:
            if rec.origin:
                so = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
                if so:
                    rec.sale_order_id = so.id
                else:
                    rec.sale_order_id = False
            else:
                rec.sale_order_id = False
