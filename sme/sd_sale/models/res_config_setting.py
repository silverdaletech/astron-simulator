# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_complete_so = fields.Boolean(
        string='Complete Sale Order',
        required=False)

    module_sd_signed_so = fields.Boolean(
        string='Signed Sale order',
        required=False)

    # module_sd_sale_mrp = fields.Boolean(
    #     string='MO Description',
    #     required=False)

    module_sd_sale_project = fields.Boolean(
        string='Project Description from SO', required=False)

    sale_price_change = fields.Boolean(
        string='Sale price change', config_parameter='sd_sale.sale_price_change', required=False)

    module_sd_mrp_status = fields.Boolean(
        string='MRP Status',
        required=False)

    module_sd_credit_management = fields.Boolean(string='Credit Management')
    module_sd_so_analytic = fields.Boolean(string='Sale Default Analytic Rules')
    module_sd_sale_commission = fields.Boolean(string='Silverdale Sale Commission')
    module_sd_sale_coupons_and_promotions = fields.Boolean(string='Coupons and Promotions')
    module_sd_sale_crm = fields.Boolean(string='Sales on CRM')
