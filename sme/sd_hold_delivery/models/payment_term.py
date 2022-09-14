
from odoo import _, api, fields, models, tools


class PaymentTermUser(models.Model):
    _inherit = 'account.payment.term'

    hold_delivery_till_payment = fields.Boolean(default=False, copy=False, help="If this is checked, Hold Delivery check on Salesorder will automatically be true")
    applied_operation_types = fields.Many2many('stock.picking.type', string='Apply to these Operations Types')
