# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    planned_date = fields.Date(string='Planned End Date')
    note = fields.Text(string="Note")
