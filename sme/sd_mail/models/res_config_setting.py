# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_mail_compose = fields.Boolean(
        string='Send Message Composer',
        required=False)

    module_sd_mail_ext = fields.Boolean(
        string='Mail Extension',
        required=False)

    module_sd_bcc_mail = fields.Boolean(
        string='BCC Email',
        required=False)

    module_sd_company_mail = fields.Boolean(
        string='Company Based Notifications',
        required=False)

    module_sd_activity_multiusers = fields.Boolean(
        string='Activity For Multiple Users',
        required=False)
