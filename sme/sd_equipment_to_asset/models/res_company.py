# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    is_purchase_equipment = fields.Boolean()
    purchase_equipment = fields.Selection([
        ('receipt', 'Receipt confirmation'),
        ('bill', 'Bill posting'),
        ], string="Equipment is created upon", )

