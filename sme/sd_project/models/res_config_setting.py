# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    restrict_over_spend_hour = fields.Boolean(string="Restrict over spend hours",
                                              config_parameter='sd_project.restrict_over_spend_hour')

    module_sd_project_timesheet = fields.Boolean(string='Silverdale Project Timesheet')
