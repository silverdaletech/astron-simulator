from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_validation_failed = fields.Boolean(
        string='Partner validation Failed', related="partner_id.validation_failed",store=True,
        required=False)
    partner_validation_message = fields.Char(
        string='Partner_validation_message', related="partner_id.validation_message",store=True,
        required=False)
    partner_date_validated = fields.Datetime(
        string='Partner_date_validated', related="partner_id.date_validated",store=True,
        required=False)

    def button_validate_partner_address(self):
        for order in self:
            if order and order.partner_id and order.partner_invoice_id and order.partner_shipping_id:
                return order.partner_shipping_id.button_validate_address()
