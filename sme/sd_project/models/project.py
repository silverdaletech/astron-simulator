# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from collections import defaultdict
from odoo.addons.project.models.project import PROJECT_TASK_READABLE_FIELDS

PROJECT_TASK_READABLE_FIELDS.add("is_timesheet_portal")

class ProjectFormSt(models.Model):
    _inherit = 'project.project'

    task_count_with_subtasks_custom = fields.Integer(compute='_compute_task_count')
    project_stage_type_id = fields.Many2one('project.stages.type', string='Project Stages Type')

    # moved from sd_project_portal
    is_timesheet_portal = fields.Boolean(string="Show TimeSheet On Portal")

    def _compute_task_count_custom(self):
        return super(ProjectFormSt, self)._compute_task_count()

    @api.model
    def create(self, values):
        project_create = super(ProjectFormSt, self).create(values)
        for rec in project_create.project_stage_type_id.stages_line:
            task_type = self.env['project.task.type'].search([('name', '=', rec.name)], limit=1)
            if task_type:
                projects = project_create + task_type.project_ids
                task_type.write({
                    'project_ids': [(6, 0, projects.mapped('id'))]
                })
        return project_create
    
