# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_revalidate = fields.Selection(
        string='Auto Revalidate',
        selection=[
            ('week', 'Weeks'),
            ('months', 'Months'),
            ('years', 'Years'), ],
        required=False, )
    number_of_period = fields.Integer(
        string='Number Of Period',
        required=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    usps_user_id = fields.Char(
        string='Sale price change', config_parameter='sd_address_validation.usps_user_id', required=False)
    address_check_on_creation = fields.Boolean(
        string='Address Check On Creation', config_parameter='sd_address_validation.address_check_on_creation',
        required=False)
    auto_revalidate = fields.Selection(
        string='Auto Revalidate',
        selection=[
            ('week', 'Weeks'),
            ('months', 'Months'),
            ('years', 'Years'), ],
        required=False, related="company_id.auto_revalidate", readonly=False,)
    number_of_period = fields.Integer(
        string='Number Of Period',
        required=False , related="company_id.number_of_period", readonly=False)
