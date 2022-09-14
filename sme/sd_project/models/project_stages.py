# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectStagesType(models.Model):
    _name = 'project.stages.type'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Project Stages"

    name = fields.Char(string='Stages Type', required=True)
    stages_line = fields.Many2many('project.task.type', string='Stages', required=True)




