# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('complete', 'Complete'),('cancel',)
    ])

    def action_close_sale_order(self):
        """Change sale order state to closed"""
        for rec in self:
            rec.state = 'complete'
