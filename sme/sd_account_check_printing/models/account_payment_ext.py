# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date

INV_LINES_PER_STUB = 9


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _check_make_stub_pages(self):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.

            We include the reconciled data as separated lines in stub-lines
        """
        self.ensure_one()

        def prepare_vals(invoice, partials):
            number = ' - '.join([invoice.name, invoice.ref] if invoice.ref else [invoice.name])

            reconciled_info_values = invoice.sudo()._get_reconciled_info_JSON_values()
            reconciled_info = []

            for rec in reconciled_info_values:
                if self.id == rec.get('account_payment_id', False):
                    continue
                reconciled_info.append(rec)

            if invoice.is_outbound():
                invoice_sign = 1
                partial_field = 'debit_amount_currency'
            else:
                invoice_sign = -1
                partial_field = 'credit_amount_currency'

            if invoice.currency_id.is_zero(invoice.amount_residual):
                amount_residual_str = '-'
            else:
                amount_residual_str = formatLang(self.env, invoice_sign * invoice.amount_residual,
                                                 currency_obj=invoice.currency_id)

            values = [{
                'due_date': format_date(self.env, invoice.invoice_date_due),
                'number': number,
                'amount_total': formatLang(self.env, invoice_sign * invoice.amount_total,
                                           currency_obj=invoice.currency_id),
                'amount_residual': amount_residual_str,
                'amount_paid': formatLang(self.env, invoice_sign * sum(partials.mapped(partial_field)),
                                          currency_obj=self.currency_id),
                'currency': invoice.currency_id,
            }]
            for rec in reconciled_info:
                move_type_text = 'Payment'
                payment_method = ''
                if rec.get('move_id'):
                    move_type = self.env['account.move'].search([('id', '=', rec.get('move_id'))]).move_type
                    if move_type == 'in_refund':
                        move_type_text = 'Credit Note'
                if rec.get('payment_method_name'):
                    payment_method = f"({rec.get('payment_method_name')})"
                vals = {
                    'due_date': '',
                    'number': '',
                    'amount_total': f"{move_type_text} {payment_method}",
                    'amount_residual': rec.get('ref', False),
                    'amount_paid': rec.get('amount', False),
                    'currency': '',
                }

                values.append(vals)
            return values

        # Decode the reconciliation to keep only invoices.
        term_lines = self.line_ids.filtered(lambda line: line.account_id.internal_type in ('receivable', 'payable'))
        invoices = (
                term_lines.matched_debit_ids.debit_move_id.move_id + term_lines.matched_credit_ids.credit_move_id.move_id) \
            .filtered(lambda x: x.is_outbound())
        invoices = invoices.sorted(lambda x: x.invoice_date_due or x.date)

        # Group partials by invoices.
        invoice_map = {invoice: self.env['account.partial.reconcile'] for invoice in invoices}
        for partial in term_lines.matched_debit_ids:
            invoice = partial.debit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial
        for partial in term_lines.matched_credit_ids:
            invoice = partial.credit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial

        # Prepare stub_lines.
        if 'out_refund' in invoices.mapped('move_type'):
            stub_lines = [{'header': True, 'name': "Bills"}]
            stub_lines += [prepare_vals(invoice, partials)
                           for invoice, partials in invoice_map.items()
                           if invoice.move_type == 'in_invoice']
            stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += [prepare_vals(invoice, partials)
                           for invoice, partials in invoice_map.items()
                           if invoice.move_type == 'out_refund']
        else:
            stub_lines = [prepare_vals(invoice, partials)
                          for invoice, partials in invoice_map.items()
                          if invoice.move_type == 'in_invoice']
        lines = []
        for stub in stub_lines:
            if not isinstance(stub, list):
                if stub.get('header', False):
                    lines.append(stub)
            else:
                for s in stub:
                    lines.append(s)

        stub_lines = lines

        # Crop the stub lines or split them on multiple pages
        if not self.company_id.account_check_printing_multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []

            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i + INV_LINES_PER_STUB and stub_lines[i + INV_LINES_PER_STUB - 1].get('header'):
                    num_stub_lines = INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i + num_stub_lines])
                i += num_stub_lines

        return stub_pages
