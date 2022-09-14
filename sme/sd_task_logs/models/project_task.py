import pdb
from datetime import datetime

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    planned_hours_ids = fields.One2many(
        comodel_name='task.planned.hour',
        inverse_name='task',
        string='Planned hours',
        required=False)
    stage_log_ids = fields.One2many(
        comodel_name='stage.log',
        inverse_name='task',
        string='Stage_log_ids',
        required=False)

    def write(self, vals):
        """
        This function picks changes when record is created from project.task model and create new record in
         the 'stage.log' and 'task.planned.hour' models and update them if changes are made vice versa
        """
        for rec in self:
            if vals.get('stage_id'):
                project_type_id = self.env['project.task.type'].search([('id', '=', vals.get('stage_id'))])
                history_data = {
                    'stage_from': rec.stage_id.name,
                    'stage_to': project_type_id and project_type_id.name,
                    'user': self.env.user.id,
                    'time': datetime.now(),
                    'task': rec.id,
                }
                self.env['stage.log'].create(history_data)

            if vals.get('planned_hours'):
                hours_data = {
                    'hour_from': rec.planned_hours,
                    'hour_to': vals.get('planned_hours'),
                    'user': self.env.user.id,
                    'time': datetime.now(),
                    'task': rec.id,
                }
                self.env['task.planned.hour'].create(hours_data)

        res = super(ProjectTask, self).write(vals)
        return res
