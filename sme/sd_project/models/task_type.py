# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _name = 'task.type'
    _description = 'Task type'

    name = fields.Char(string='Name')
    sequence = fields.Integer(string='Sequence')
    active = fields.Boolean(string='Active', default=True)
    project_task_ids = fields.One2many('project.task', 'task_type_id', string='Tasks', readonly=True)
