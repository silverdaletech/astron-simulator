from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_credit(self):
        """
        This function will compute credit of customer including child as well.
        Credit will compute  as total of overdue invoices or if sale order is confirm and  invoice is not created yet
        then it
        will add this payment as well in partner credit.
        """
        for rec in self:
            # Previous Receivable
            credit = rec.credit
            # All Confirm Sale order
            all_partners = self.search([('id', 'child_of', rec.ids)])
            all_partners.read(['parent_id'])

            confirm_so = self.env['sale.order'].search(
                [('partner_id', 'in', all_partners.ids), ('state', 'in', ('sale', 'done'))]
            )

            confirm_so_amount = 0
            for so in confirm_so:
                so_amount = sum(so.mapped('amount_total'))
                inv_amount = sum(so.invoice_ids.filtered(lambda x: x.state != 'cancel').mapped('amount_total_signed'))
                # Ignore sale order amount if total invoiced amount is greater then sale order amount
                if inv_amount > so_amount:
                    continue
                else:
                    # Get remaining sale order amount
                    confirm_so_amount += so_amount - inv_amount

            # Get draft invoices for credit limit
            account_move_draft = self.env['account.move'].search([
                ('partner_id', 'in', all_partners.ids),
                ('state', '=', 'draft'),
                ('move_type', '=', 'out_invoice')
            ])
            account_move_draft = sum(account_move_draft.mapped('amount_total_signed'))

            # Compute credit limit
            rec.total_credit_used = credit + confirm_so_amount + account_move_draft

    total_credit_used = fields.Monetary(
        compute='_compute_credit',
        string='Total Credit Used',
        help='Total credit used by the partner')
    credit_hold = fields.Boolean(
        string='Credit Hold',
        help='True, if the credit is on hold',
        tracking=True,
        copy=False,
    )
