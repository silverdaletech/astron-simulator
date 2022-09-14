# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    sales_commission = fields.Boolean(
        string='Sales Commission', implied_group='sd_sale_commission.group_sale_commission')

    commission_criteria = fields.Selection(
        string='Commission Criteria',
        selection=[
                ('fixed', 'Fixed Percentage'),
                ('by_ammount', 'By amount brackets')
            ])

    commission_generated_upon = fields.Selection(
        string='Commission is generated upon',
        selection=[
                ('invoice_issue', 'Invoice issuance'),
                ('invoice_payment', 'Invoice payment')
            ])
    commission_base_amount = fields.Selection(
        string='Commission base amount',
        selection=[
                ('with_tax', 'With Tax'),
                ('without_tax', 'Without Tax')
            ])


class ResConfigSettingsCommission(models.TransientModel):
    _inherit = 'res.config.settings'

    group_sales_commission = fields.Boolean(
        string='Sale Commissions', related='company_id.sales_commission',
        readonly=False, implied_group='sd_sale_commission.group_sale_commission')

    commission_criteria = fields.Selection(
        string='Commission Criteria',
        related='company_id.commission_criteria',
        readonly=False)
    
    commission_generated_upon = fields.Selection(
        string='Commission is generated upon',
        related='company_id.commission_generated_upon',
        readonly=False)

    commission_base_amount = fields.Selection(
        string='Commission base amount',
        related='company_id.commission_base_amount',
        readonly=False)
    
    group_commission_fixed = fields.Boolean(implied_group='sd_sale_commission.group_commission_fixed')
    group_commission_by_amount_brackets = fields.Boolean(implied_group='sd_sale_commission.group_commission_by_amount_brackets')

    @api.onchange('group_sales_commission')
    def _onchange_group_sales_commission(self):
        for rec in self:
            if not rec.group_sales_commission:
                rec.commission_criteria = False
                rec.commission_generated_upon = False
                rec.commission_base_amount = False

    @api.onchange('commission_criteria')
    def _onchange_commission_criteria(self):
        if self.commission_criteria == 'by_ammount':
            self.group_commission_fixed = False
            self.group_commission_by_amount_brackets = True
        elif self.commission_criteria == 'fixed':
            self.group_commission_fixed = True
            self.group_commission_by_amount_brackets = False
