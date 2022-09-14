# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_type_id = fields.Many2one('task.type')
    client_id = fields.Many2one('res.partner', string="Client", related='partner_id.parent_id', store=True)
    project_stage_id = fields.Many2one(comodel_name='project.project.stage', related="project_id.stage_id", string="Project status", store=True, groups="project.group_project_stages")

    # def compute_project_status(self):
    #     for rec in self:
    #         rec.project_stage_id = False
    #         if rec.project_id and rec.project_id.stage_id:
    #            print('')

    def write(self, vals):
        effective_hours = 0
        if vals.get('timesheet_ids'):
            effective_hours = self.effective_hours
        res = super(ProjectTask, self).write(vals)
        if vals.get('timesheet_ids'):
            new_effective_hours = self.effective_hours
            if self.planned_hours > 0 and effective_hours != new_effective_hours and self.env[
                'ir.config_parameter'].sudo().get_param('sd_project.restrict_over_spend_hour') == "True":
                if self.effective_hours > self.planned_hours:
                    raise ValidationError(
                        ' Total time spent is going above the time planned for this task.\n Please edit the planned time for the task.')

        return res


class ProjectProjectType(models.Model):
    _inherit = 'project.task.type'

    is_opened = fields.Boolean(string="Open Stage", help="Tasks in this stage are considered as opened.")
    is_cancelled = fields.Boolean(string="Cancelled Stage", help="Tasks in this stage are considered as cancelled.")
