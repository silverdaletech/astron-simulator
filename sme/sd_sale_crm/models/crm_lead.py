# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    lead_line_ids = fields.One2many(
        comodel_name="crm.lead.line", 
        inverse_name="lead_id", 
        string="Lead Lines"
    )
    total_estimated_revenue  = fields.Monetary(
        string="Total Estimated Revenue", 
        compute='_compute_total_line_ammount',
        currency_field='company_currency',
        tracking=True,)
    total_planned_revenue  = fields.Monetary(
        string="Total Planned Revenue", 
        currency_field='company_currency',
        compute='_compute_total_line_ammount',
        tracking=True,)
    total_actual_revenue  = fields.Monetary(
        string="Total Actual Revenue",
        currency_field='company_currency',
        compute='_compute_total_line_ammount',
        tracking=True,)

    #-------------------------------------
    # Base Functions
    #-------------------------------------
    
    def action_new_quotation(self):
        action = super(CRMLead, self).action_new_quotation()
        products = []
        for line in self.lead_line_ids.filtered(lambda x: x.sale_type == 'planned'):
            if line.product_qty - line.actual_qty_sold > 0:
                products.append((0, 0, {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'product_uom_qty': line.product_qty - line.actual_qty_sold ,
                                'product_uom': line.uom_id.id,
                                'price_unit': line.price_offered,
                                'crm_lead_line_id': line.id
                                }))
        action['context']['default_order_line'] =products
        return action

    #------------------------------------
    # Compute Api
    #------------------------------------
    @api.depends('lead_line_ids')
    @api.onchange('lead_line_ids')
    def _compute_total_line_ammount(self):
        for rec in self:
            rec.total_estimated_revenue = sum(rec.lead_line_ids.mapped('estimated_revenue'))
            rec.total_planned_revenue = sum(rec.lead_line_ids.mapped('planned_revenue'))
            rec.total_actual_revenue = sum(rec.lead_line_ids.mapped('actual_revenue'))
