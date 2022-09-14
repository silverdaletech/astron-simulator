# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_based_notifications = fields.Boolean(string="Company Based Notifications",
                                                 config_parameter='sd_company_mail.company_based_notifications')

