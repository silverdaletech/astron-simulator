# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_helpdesk_timesheet = fields.Boolean(
        string='Helpdesk timesheet')
    module_sd_helpdesk_crm = fields.Boolean(
        string='Create Opportunities from Ticket')

