# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import math


class WorkStream(models.Model):
    _name = 'work.stream'
    _description = 'Work Stream'
    _order = 'sequence'

    name = fields.Char('Name')
    active = fields.Boolean(string='Active', default= True)
    sequence = fields.Integer(string='Sequence')
    process_ids = fields.One2many(
        comodel_name='work.stream.processes',
        inverse_name='work_stream_id',
        string='Processes')


class WorkStreamProcesses(models.Model):
    _name = 'work.stream.processes'
    _description = 'Processes'
    _order = 'sequence'

    name = fields.Char('Name')
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence')
    work_stream_id = fields.Many2one('work.stream', string='Work Stream', required=True, ondelete='cascade')
    process_desc = fields.Html(string="Description")
    luci_chart_url = fields.Char(string='Chart Url')
    luci_chart = fields.Text(compute='_compute_chart')

    @api.onchange('luci_chart_url')
    def _compute_chart(self):
        for rec in self:
            luci_chart = ''
            if rec.luci_chart_url:
                luci_chart = '<div style="width: 960px; height: 720px; margin: 10px; position: relative;"> ' \
                             '<iframe allowfullscreen="1" frameborder="0" style="width:1000px; height:720px" src="' + rec.luci_chart_url + '" id="MSKX7Jna2c80"></iframe>' \
                                                                                                                                           '</div>'
            rec.luci_chart = luci_chart


