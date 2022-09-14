import pdb
from datetime import datetime

from odoo import models, fields, api


class StagesLog(models.Model):
    _name = 'stage.log'
    _description = 'Will log the stage move'
    _rec_name = 'task'

    user = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=False)
    stage_from = fields.Char(string="Stage From")
    stage_to = fields.Char(string="Stage To")
    time = fields.Datetime()
    task = fields.Many2one(comodel_name='project.task', string='Task', required=False)
    task_id = fields.Integer(string="Task ID", related='task.id', store=True)


