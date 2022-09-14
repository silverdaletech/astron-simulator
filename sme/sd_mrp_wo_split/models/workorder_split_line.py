# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class WorkorderSplitLine(models.Model):
    _name = 'workorder.split.line'
    _description = 'Workorder Split Line'

    name = fields.Char(string="Operation", required=True)
    workcenter_id = fields.Many2one('mrp.workcenter')
    workorder_id = fields.Many2one('mrp.workorder')
    operation_id = fields.Many2one('mrp.routing.workcenter')
    qty = fields.Float()
    is_done = fields.Boolean()
