# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_maintenance_mode = fields.Boolean(
        string='Website Maintenance Mode', config_parameter='sd_maintenace_mode.website_maintenance_mode',
        required=False)
    upgrade_end_date = fields.Datetime(
        string='Upgrade end time', related='company_id.upgrade_end_date', readonly=False,
        required=False)
    admin_user = fields.Many2one(
        comodel_name='res.users', related='company_id.admin_user',readonly=False,
        string='Admin user',
        required=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    upgrade_end_date = fields.Datetime(
        string='Upgrade end time',
        required=False)

    admin_user = fields.Many2one(
        comodel_name='res.users',
        string='Admin user',
        required=False)
