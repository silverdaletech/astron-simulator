# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_disallow_negative_stock = fields.Boolean(
        string='Prevent Negative Inventory',
        required=False)

    module_sd_stock_status = fields.Boolean(
        string='Delivery Status',
        required=False)

    module_sd_stock_invoice = fields.Boolean(
        string='Create Invoice from Stock')

    module_sd_stock_delivery = fields.Boolean(
        string='Shipping on Delivery order')
