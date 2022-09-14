# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    product_in_opportunity = fields.Boolean()
    crm_product_price_rule = fields.Selection([
        ('roles', 'Manager/User Roles'),
        ('team', 'Team Member'),
        ],string="Custom Pricing to be configured on",
        required=False,)
