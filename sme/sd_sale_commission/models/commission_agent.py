# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CommissionAgent(models.Model):
    _name = 'sale.commission.agent'
    _description = 'Commission Agent'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Related Contact')
    commission_expense_acc_id = fields.Many2one('account.account', string='Commission Expense Account')
    commission_percentage = fields.Integer(string='Commission Percentage')
    line_ids = fields.One2many('sale.commission.agent.line', inverse_name='sale_commission_id', string='Line ids')

    @api.constrains('commission_percentage')
    def _constrains_commission_percentage(self):
        for rec in self:
            if rec.env.user.has_group('sd_sale_commission.group_commission_fixed') and rec.commission_percentage < 1 or rec.commission_percentage > 100:
                raise UserError(_('The commission percentage should be between 1 to 100.'))


class CommissionAgentLine(models.Model):
    _name = 'sale.commission.agent.line'
    _description = 'Commission Agent Line'

    amount_from = fields.Float(string="Amount From",tracking=True)
    amount_to = fields.Float(string="Amount To", tracking=True)
    
    commission_percentage = fields.Integer(
        string='Commission Percentage')
    sale_commission_id = fields.Many2one('sale.commission.agent', string='Sale Commission')

    @api.constrains('commission_percentage', 'amount_to', 'amount_from')
    def _constrains_commission_percentage(self):
        for rec in self:
            if rec.amount_to < 1:
                raise UserError(_('Amount to cannot be less then zero(0).'))
            if rec.amount_to < rec.amount_from:
                raise UserError(_('"Amount From" must be greater than "Amount to".'))
            if rec.commission_percentage < 1 or rec.commission_percentage > 100:
                raise UserError(_('The commission percentage should be between 1 to 100.'))
