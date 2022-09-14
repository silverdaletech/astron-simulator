# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    hide_task_type_portal = fields.Boolean(string='Task Type Hide Functionality', implied_group='sd_project_timesheet.group_hide_task_type_portal' )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_hide_task_type_portal = fields.Boolean(string="Task Type Hide Functionality", related='company_id.hide_task_type_portal',
                                                 readonly=False, implied_group='sd_project_timesheet.group_hide_task_type_portal')
