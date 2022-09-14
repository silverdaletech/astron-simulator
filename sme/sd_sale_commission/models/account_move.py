# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    commissionable_line = fields.Boolean(string='Commission-able line', copy=False)
    commission_line_id = fields.Many2one('sale.commission.line', copy=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_commission_id = fields.Many2one('sale.commission.agent',
        string='Commission Agent', copy=False)
    settlement_id = fields.Many2one('sale.commission.settlement', copy=False)
    is_commissionable = fields.Boolean(
        string='Is Commissionable', copy=False, compute="_compute_is_commissionable")

    def create_commission_line(self):
        line_ids = self.mapped('line_ids').filtered(
            lambda line: line.commissionable_line and not line.commission_line_id)

        if line_ids and self.sale_commission_id and self.company_id.sales_commission:
            for line in line_ids:
                price_total = 0

                if line.company_id.commission_base_amount == 'with_tax':
                    price_total = line.price_total
                elif line.company_id.commission_base_amount == 'without_tax':
                    price_total = line.price_subtotal

                commission_amount = 0
                if line.company_id.commission_criteria == 'fixed':
                    commission_amount = price_total * (self.sale_commission_id.commission_percentage / 100)
                elif line.company_id.commission_criteria == 'by_ammount':
                    amount_line = self.sale_commission_id.line_ids.filtered(lambda x: x.amount_from <= price_total and  x.amount_to >= price_total)
                    if amount_line:
                        commission_percentage = amount_line[0].commission_percentage
                        commission_amount = price_total * (commission_percentage / 100)

                values = {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'unit_price': line.price_unit,
                    'qty': line.quantity,
                    'subtotal': line.price_subtotal,
                    'commissionable_amount': price_total,
                    'commission_amount': commission_amount,
                    'move_line_id': line.id,
                    'agent_id': self.sale_commission_id.id
                }

                if price_total != 0 and commission_amount != 0:
                    sl = self.env['sale.commission.line'].create(values)
                    line.commission_line_id = sl.id

            sl = self.env['sale.commission.line'].search([('move_line_id', 'in', line_ids.ids)])

            if sl:
                values = {
                    'name': self.name,
                    'commission_agent': self.sale_commission_id.id,
                    'invoice_id': self.id,
                    'partner_id': self.sale_commission_id.partner_id.id,
                    'commission_expense_acc_id': self.sale_commission_id.commission_expense_acc_id.id,
                    'total_invoice_amount': self.amount_total_signed
                }

                scl = self.env['sale.commission.record'].create(values)
                sl.write({'commission_record_id': scl.id})
    
    def action_post(self):
        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(AccountMove, self).action_post()
        if self.company_id.commission_generated_upon == 'invoice_issue' and self.move_type == 'out_invoice':
            self.create_commission_line()
        return res
    
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()

        for move in self:
            if move.payment_state in ['paid','in_payment'] and  move.company_id.commission_generated_upon == 'invoice_payment':
                move.create_commission_line()
            elif move.payment_state not in ['paid','in_payment'] and move.company_id.commission_generated_upon == 'invoice_payment':
                for line in move.line_ids:
                    msg = _('Payment have been unlinked from %s.', move.name)
                    move.unlink_commission_record(msg)
        return res

    @api.depends('invoice_line_ids')
    @api.onchange('invoice_line_ids')
    def _compute_is_commissionable(self):
        for rec in self:
            if any(line.product_id.commissionable == True for line in rec.invoice_line_ids) and rec.move_type == 'out_invoice':
                rec.is_commissionable =True
            else:
                rec.is_commissionable = False

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for rec in self:
            if rec.move_type == 'out_invoice':
                msg = _('Related Invoice %s have been reset.', rec.name)
                rec.unlink_commission_record(msg)
        return res

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for rec in self:
            if rec.move_type == 'out_invoice':
                msg = _('Related Invoice %s have been cancelled', rec.name)
                rec.unlink_commission_record(msg)
        return res

    def unlink_commission_record(self, msg):
        for line in self.line_ids:
            rec = line.sudo().commission_line_id.filtered(lambda x: x.state == 'pending').commission_record_id
            if rec:
                scl = rec.settlement_line_id.commission_settlement_id
                if scl:
                    scl.message_post(body=msg)
            rec.unlink()
