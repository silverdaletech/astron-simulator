# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sd_timesheet_min_duration = fields.Integer('Minimal Duration', default=15, config_parameter='sd_crm_timesheet.sd_timesheet_min_duration')
    sd_timesheet_rounding = fields.Integer('Round up', default=15, config_parameter='sd_crm_timesheet.sd_timesheet_rounding')
