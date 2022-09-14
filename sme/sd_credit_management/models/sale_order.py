from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import exception_to_unicode


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_limit = fields.Float(
        string='Credit Limit', related='partner_id.credit_limit',
        required=False)
    override_credit_limit = fields.Boolean(
        string='Override Credit Limit',
        copy=False,
        tracking=True,
    )
    over_credit = fields.Boolean(
        string='Over Credit',
        copy=False,
        readonly=True
    )
    commercial_partner_id = fields.Many2one('res.partner',
                                            related='partner_id.commercial_partner_id',
                                            readonly=True, )
    hold_delivery_till_payment = fields.Boolean(help="If True, then holds the DO until  \
                                        invoices are paid and equals to the total amount on the SO")


    def check_partner_credit_limit(self):
        """
        This function will check partner credit limit over or not on sale order,
        if sale order or total  invoice overdue exceed credit limit of partner then it will
        return validation message.
        """
        if not self._context.get('website_order_tx', False):
            partner = self.partner_id.commercial_partner_id
            for sale in self:
                invoices = sale.invoice_ids.filtered(lambda x: x.state == 'posted')
                invoice_amount_total = sum(invoices.mapped('amount_total_signed'))
                invoice_due_amount = sum(invoices.mapped('amount_residual'))
                paid_amount = invoice_amount_total - invoice_due_amount

                inv_amount = sum(
                    sale.invoice_ids.filtered(lambda x: x.state not in ['cancel', 'draft']).mapped('amount_total'))
                if (partner.credit_limit > 0) and not sale.override_credit_limit:
                    if sale.override_credit_limit or paid_amount >= sale.amount_total:
                        return True
                    else:
                        inv_amount = sum(
                            sale.invoice_ids.filtered(lambda x: x.state != 'cancel').mapped('amount_total_signed'))
                        actual_credit_used = sale.amount_total - inv_amount + partner.total_credit_used
                        if not sale.override_credit_limit and actual_credit_used > partner.credit_limit:
                            raise UserError(
                                _("Over Credit Limit!\n"
                                  "Credit Limit: {0}{1:.2f}\n"
                                  "Total Credit Balance (Previous used): {0}{2:.2f}\n"
                                  "Total this order: {0}{3:.2f}\n"
                                  "Total Credit Use with this order: {0}{4:.2f}\n"
                                  "You Can Use Total Remaining Credit upto this Amount: {0}{5:.2f}".format(
                                    sale.currency_id.symbol,
                                    partner.credit_limit,
                                    partner.total_credit_used,
                                    sale.amount_total,
                                    actual_credit_used,
                                    (partner.credit_limit - partner.total_credit_used),
                                )
                                ))
            return True

    def action_confirm(self):
        for order in self:
            partner = order.partner_id.commercial_partner_id
            try:
                order.over_credit = False
                order.check_partner_credit_limit()

            except UserError as e:
                order.over_credit = True
                return {
                    'name': 'Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'partner.credit.limit.warning',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {'default_message': e.name}
                }
        return super(SaleOrder, self).action_confirm()


    @api.onchange('partner_id')
    def onchange_partner_id_credit_warning(self):
        """
        This function will recheck invoice overdue of partner if partner change.
        """
        try:
            if self.partner_id:
                self.check_partner_credit_limit()
        except Exception as e:
            return {
                'warning': {
                    'title': _("Warning!"),
                    'message': exception_to_unicode(e),
                }
            }

    def action_cancel(self):
        """
        This function will reset over_credit and override_credit_limit flags if we cancel sale order.
        """
        res = super(SaleOrder, self).action_cancel()
        self.write({
            'over_credit': False,
            'override_credit_limit': False,
        })
        return res

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
        elif total >= self.amount_total:
            return True
        else:
            return False
