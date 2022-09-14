# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    """
    res.partner model is inherited to add following field and display a page on contact form view
    """
    _inherit = 'res.partner'

    commission_agent_id = fields.Many2one('sale.commission.agent',
        string='Commission Agent')
