# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Company(models.Model):
    _inherit = 'res.company'

    module_sd_crm_floe = fields.Boolean(
        string='Level of Efforts',
        required=False)

    crm_default_activity = fields.Many2one('mail.activity.type', string='Default Crm Activity')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_crm_floe = fields.Boolean(
        string='Level of Efforts', related="company_id.module_sd_crm_floe", readonly=False,
        required=False)

    crm_default_activity = fields.Many2one('mail.activity.type', string='Default Crm Activity', config_parameter="sd_crm.crm_default_activity")
