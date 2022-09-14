from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import exception_to_unicode


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hold_delivery_till_payment = fields.Boolean(help="If True, then holds the DO until  \
                                        invoices are paid and equals to the total amount on the SO", related='payment_term_id.hold_delivery_till_payment')

    def check_invoice_fully_paid(self):
        self.ensure_one()
        downpayment_amount = sum(self.mapped('order_line').filtered(lambda x: x.is_downpayment == True)
                                 .invoice_lines.mapped('move_id').filtered(lambda x: x.move_type in ['out_invoice']
                                                                                     and x.payment_state in [
                                                                                         'in_payment', 'paid']).mapped(
            'amount_total'))
        invoice_amount = sum(self.invoice_ids.filtered(lambda x: x.move_type in ['out_invoice']
                                                                 and x.payment_state in ['in_payment', 'paid']).mapped(
            'amount_total'))
        total = downpayment_amount + invoice_amount
        if invoice_amount >= self.amount_total or downpayment_amount >= self.amount_untaxed:
            return True
        # elif total >= self.amount_total:
        #     return True
        else:
            return False
