# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    floe_total = fields.Float(compute='_compute_floe_total', string='FLOE Total')
    floe_c = fields.Float(string='FLOE C')
    floe_d = fields.Float(string='FLOE D')
    floe_q = fields.Float(string='FLOE Q')

    @api.onchange('floe_c', 'floe_d', 'floe_q')
    def _compute_floe_total(self):
        for rec in self:
            rec.floe_total = rec.floe_c + rec.floe_d + rec.floe_q

