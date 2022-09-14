# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCountry(models.Model):
    _inherit = 'res.company'

    invoice_on_delivery = fields.Boolean(string="Invoice on delivery?")
    delivery_invoice_auto_reconcile = fields.Boolean(string="Autoreconcile the payment")
    delivery_invoice_email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Confirmation Email Template',
        domain="[('model', '=', 'account.move')]",
        help="Email sent to the customer once the order is paid."
    )
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_on_delivery = fields.Boolean(
        string='Invoice on delivery?', related="company_id.invoice_on_delivery", readonly=False)

    delivery_invoice_auto_reconcile = fields.Boolean(string="Autoreconcile the payment", related="company_id.delivery_invoice_auto_reconcile", readonly=False)

    delivery_invoice_email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Confirmation Email Template',
        domain="[('model', '=', 'account.move')]",
        help="Email sent to the customer once the order is paid.",
        related="company_id.delivery_invoice_email_template_id",
        readonly=False
    )