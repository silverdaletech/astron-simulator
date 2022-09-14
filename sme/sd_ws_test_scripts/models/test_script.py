# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class TestScriptInherit(models.Model):
    _inherit = 'project.test.script'

    process_id = fields.Many2one('work.stream.processes', string='Process')
    work_stream_id = fields.Many2one('work.stream', string='Work Stream', related='process_id.work_stream_id', store=True)

