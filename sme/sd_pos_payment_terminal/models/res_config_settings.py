# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError,ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    """
        "res.config.settings" model is inherited to add a boolean field module_sd_pos_stripe_payment_terminal in the POS 'Payment Terminals' section
            to install and uninstall the module sd_pos_stripe_payment_terminal
    """
    module_sd_pos_stripe_payment_terminal = fields.Boolean(string="Strip Payment Terminal", help="Here transactions are processed by Strip Cards.")

    module_sd_pos_square_payment_terminal = fields.Boolean(string="Square Payment Terminal", help="Here transactions are processed by Square Terminal.")

    @api.onchange('module_sd_pos_square_payment_terminal')
    def check_square(self):
        """to check either Square module exist or not"""
        if self.module_sd_pos_square_payment_terminal:
            module = self.env['ir.module.module'].search([('name', '=', 'sd_pos_square_payment_terminal')])
            if not module:
                raise ValidationError('PLease Contact on "info@silverdaletech.com" '
                                      'to get Square Payment terminal Module')

    @api.onchange('module_sd_pos_stripe_payment_terminal')
    def check_stripe(self):
        """To check module either stripe module exist or not"""
        if self.module_sd_pos_stripe_payment_terminal:
            module = self.env['ir.module.module'].search([('name', '=', 'sd_pos_stripe_payment_terminal')])
            if not module:
                raise ValidationError(
                    'PLease Contact on "info@silverdaletech.com" to get Stripe Payment terminal Module')
