# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import math
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    work_stream_id = fields.Many2one('work.stream', compute='_calculate_work_stream', string='Work Stream', store=True)
    process_id = fields.Many2one('work.stream.processes', string='Process')

    @api.depends("process_id")
    def _calculate_work_stream(self):
        """
        This method will assign work stream based on process selected
        """
        for rec in self:
            rec.work_stream_id = False
            if rec.process_id and rec.process_id.work_stream_id:
                rec.work_stream_id = rec.process_id.work_stream_id

