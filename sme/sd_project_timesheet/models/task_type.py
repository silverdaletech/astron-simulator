# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.project.models.project import PROJECT_TASK_READABLE_FIELDS
PROJECT_TASK_READABLE_FIELDS.add('task_type_id.hide_from_portal')
PROJECT_TASK_READABLE_FIELDS.add('task_type_id')

class ProjectTaskType(models.Model):
    _inherit = 'task.type'

    hide_from_portal = fields.Boolean(string='Hide from Portal')

