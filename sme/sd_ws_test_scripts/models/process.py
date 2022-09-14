# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class ProcessInherit(models.Model):
    _inherit = 'work.stream.processes'

    test_script_ids = fields.One2many('project.test.script', 'process_id', string='Test Scripts')
