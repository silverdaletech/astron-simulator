# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_pos = fields.Boolean(
        string='Point of Sale Extension',
        required=False)
    module_sd_pos_payment_terminal = fields.Boolean(
        string='POS Payment Terminal Base',
        required=False)
    module_sd_pos_stripe_payment_terminal = fields.Boolean(
        string='POS Stripe Payment Terminal',
        required=False)
    module_sd_pos_sale_subscription = fields.Boolean(
        string='POS Sale Subscription',
        required=False)

