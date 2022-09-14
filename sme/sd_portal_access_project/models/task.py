# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from odoo.addons.project.models.project import PROJECT_TASK_READABLE_FIELDS

PROJECT_TASK_READABLE_FIELDS.add("is_timesheet_portal")
PROJECT_TASK_READABLE_FIELDS.add("is_show_task")
PROJECT_TASK_READABLE_FIELDS.add("is_show_task_project")
from odoo.exceptions import UserError, AccessError


class ProjectTask(models.Model):
    """
        project.task model is inherited to add three boolean fields
        'is_timesheet_portal' : this field will restricts timesheet on portal task template
        'is_show_task' : this field will restricts task on portal
        'is_show_task_project' : this field will restricts the field on task form "is_show_task"
        accordint to the value of field on project.project "privacy_visibility".
    """
    _inherit = 'project.task'


    @api.depends('project_id')
    def _compute_is_show_task(self):
        for rec in self:
            if rec.project_id:
                if rec.project_id.privacy_visibility == 'portal':
                    rec.sudo().is_show_task_project = True
                else:
                    rec.sudo().is_show_task_project = False
            else:
                rec.is_show_task_project = False

    @api.onchange('is_show_task')
    def _compute_is_timesheet_portal(self):
        for rec in self:
            if not rec.is_show_task:
                rec.is_timesheet_portal = False

    is_show_task = fields.Boolean(string="Show task on Portal", default=True)
    is_show_task_project = fields.Boolean(default=False, compute='_compute_is_show_task')
    is_timesheet_portal = fields.Boolean(string="Show Time Sheet On Portal", store=True)

    @api.onchange('project_id')
    def _on_change_project_id(self):
        """
            this method look into selected project's field "privacy_visibility" to see if its value is "portal". to update the value of
            field "is_show_task_project" . which is used to hide or show the field "is_show_task".
            this method runs on_change of project when we create or edit a task.
        """
        for rec in self:
            if rec.project_id:
                if rec.project_id.privacy_visibility != 'portal':
                    task_times_sheets = self.env['project.task'].search([('project_id', '=', rec.project_id.id)])
                    for tasks in task_times_sheets:
                        tasks.is_show_task = True

    @api.onchange('project_id','project_id.is_timesheet_portal','task_type_id','task_type_id.hide_from_portal')
    def change_task_visibility(self):
        for rec in self:
            if not rec.task_type_id.hide_from_portal:
                rec.is_show_task = True
            elif  rec.task_type_id.hide_from_portal:
                rec.is_show_task = False
            if rec.project_id.is_timesheet_portal and rec.is_show_task:
                rec.is_timesheet_portal = True
            elif not rec.project_id.is_timesheet_portal:
                rec.is_timesheet_portal = False



    def write(self, values):
        # Add code here
        if 'is_show_task' in values and values.get('is_show_task')==False:
            values['is_timesheet_portal'] = False

        return super(ProjectTask, self).write(values)



