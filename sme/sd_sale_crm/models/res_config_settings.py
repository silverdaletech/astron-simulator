# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_in_opportunity  = fields.Boolean(
        string="Products In Opportunity",
        related="company_id.product_in_opportunity",
        readonly=False,)
    crm_product_price_rule = fields.Selection(
        string="Custom Pricing to be configured on",
        related="company_id.crm_product_price_rule",
        readonly=False, required=False)
    
    group_crm_role_price = fields.Boolean(implied_group='sd_sale_crm.group_crm_price_role')
    group_crm_team_price = fields.Boolean(implied_group='sd_sale_crm.group_crm_price_team')
    group_crm_product_pipeline = fields.Boolean(implied_group='sd_sale_crm.group_crm_product_pipeline_report')

    @api.onchange('product_in_opportunity')
    def _onchange_product_in_opportunity(self):
        if not self.product_in_opportunity:
            self.crm_product_price_rule = False
            self.group_crm_product_pipeline = False
        else:
            self.group_crm_product_pipeline = True

    @api.onchange('crm_product_price_rule')
    def _onchange_crm_product_price_rule(self):
        if self.crm_product_price_rule == 'roles':
            self.group_crm_role_price = True
        else:
            self.group_crm_role_price = False
        
        if self.crm_product_price_rule == 'team':
            self.group_crm_team_price = True
        else:
            self.group_crm_team_price = False

