# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import math
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('process_id')
    def _onchange_process_id(self):
        for rec in self:
            tests = self.env['project.test.script'].search([('process_id', '=', rec.process_id.id), '|', ('partner_id', '=', rec.client_id.id), ('partner_id', '=', False)])
            rec.task_testscript_ids = [(6, 0, tests.ids)]
