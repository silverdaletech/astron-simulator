# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def link_sale_line_crm(self):
        if self.opportunity_id and self.state == 'sale':
            new_order_line = self.order_line.filtered(lambda x: not x.crm_lead_line_id and x.display_type == False)
            for line in new_order_line:
                values = {
                    'product_id': line.product_id.id if line.product_id else False,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'price_offered': line.price_unit,
                    'product_qty': 0,
                    'uom_id': line.product_uom.id,
                    'sale_type': 'unexpected',
                    'lead_id': self.opportunity_id.id
                }
                lead_line = self.env['crm.lead.line'].create(values)
                lead_line._compute_actual_qty_sold()
                line.crm_lead_line_id = lead_line.id
    
    @api.model
    def create(self, values):
        sales = super(SaleOrder, self).create(values)
        sales.link_sale_line_crm()
        return sales
    
    def write(self, values):
        sales = super(SaleOrder, self).write(values)
        self.link_sale_line_crm()
        return sales


    # def action_confirm(self):
    #     record = super(SaleOrder, self).action_confirm()
    #     record.link_sale_line_crm()
    #     return record

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    crm_lead_line_id = fields.Many2one('crm.lead.line')
    unexpected_sale = fields.Boolean(compute="_compute_unexpected_sale")

    def _compute_unexpected_sale(self):
        for rec in self:
            rec.unexpected_sale = False
            if rec.crm_lead_line_id and rec.crm_lead_line_id.sale_type == 'unexpected':
                rec.unexpected_sale = True
