# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_pos_subscriptions = fields.Boolean(string="Allow POS Subscriptions")
