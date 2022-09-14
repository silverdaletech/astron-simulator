import pdb
from datetime import datetime

from odoo import models, fields, api


class PlannedHoursLog(models.Model):
    _name = 'task.planned.hour'
    _description = 'Will log planned hours'
    _rec_name = 'task'

    user = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=False)
    hour_from = fields.Float(string="Hours From")
    hour_to = fields.Float(string="Hours To")
    time = fields.Datetime()
    task = fields.Many2one(comodel_name='project.task', string='Task', required=False)
    task_id = fields.Integer(string="Task ID", related='task.id', store=True)
