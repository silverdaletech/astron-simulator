# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleCommisionSettlement(models.Model):
    _name = 'sale.commission.settlement'
    _description = 'Sale Commission Settlement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = name = fields.Char(string='Name',
                                required=True, copy=False,
                                tracking=True, readonly=True, 
                                index=True, default=lambda self: _('New'))
    agent_ids = fields.Many2many('sale.commission.agent', tracking=True)
    date_start = fields.Datetime(string="Date From", tracking=True)
    date_end = fields.Datetime(string="Date To", tracking=True)
    commission_record_id = fields.One2many('sale.commission.record', 'commission_settlement', tracking=True)
    commission_settlement_line = fields.One2many('commission.settlement.line', 'commission_settlement_id', tracking=True)
    sale_commission_count = fields.Integer(string="Sale Commission Count", compute='_compute_sale_commission_count', tracking=True)
    account_move_count = fields.Integer(compute='_compute_sale_commission_count')
    total_payable = fields.Monetary(string="Total Payable", compute="_compute_amount", tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                default=lambda self: self.env.company.currency_id.id, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', 
                                required=True, readonly=True, tracking=True,
                                default=lambda self: self.env.company)
    state = fields.Selection([
                            ('new', 'New'),
                            ('processed', 'Processed'),
                            ('bill_created', 'Bill Created'),
                            ], default='new',tracking=True, required=True)

    @api.constrains('date_start', 'date_end')
    def _constrains_dates_coherency(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise UserError(_('The date to cannot be earlier than the date from.'))

    def _compute_sale_commission_count(self):
        for rec in self:
            rec.sale_commission_count = len(rec.commission_record_id)
            rec.account_move_count = self.env['account.move'].search_count([('settlement_id', '=', self.id)])

    def _compute_amount(self):
        for rec in self:
            rec.total_payable = sum(rec.commission_settlement_line.mapped('commission_payable'))
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.commissions.settlement') or _('New')

        result = super(SaleCommisionSettlement, self).create(vals)
        return result
    
    def action_process(self):
        for agent in self.agent_ids:
            domain = [
                ('commission_agent', '=' , agent.id),
                ('create_date', '>=', self.date_start),
                ('create_date', '<=', self.date_end),
                ('settlement_line_id', '=', False),
                ]
            rec = self.env['sale.commission.record'].search(domain)
            if rec:
                vals = {
                    'agent_id': agent.id,
                    'expense_account': agent.commission_expense_acc_id.id if agent.commission_expense_acc_id else False,
                    'commission_payable': sum(rec.mapped('commission_amount')),
                    'commission_settlement_id': self.id
                }
                scl = self.env['commission.settlement.line'].create(vals)
                rec.write({'commission_settlement': self.id, 'settlement_line_id': scl.id})
        if self.commission_settlement_line:
            self.state = 'processed'
        else:
            raise ValidationError(_("The settlement can't be processed as there are no commission lines for the speficified period."))
    
    def action_create_bill(self):
        for line in self.commission_settlement_line:
            bills = self.env['account.move']
            agent = line.agent_id
            if line.commission_payable > 0:
                if agent:
                    vals = {
                        'move_type': 'in_invoice',
                        'partner_id': agent.partner_id.id if agent.partner_id else False,
                        'invoice_date': fields.Date.today(),
                        'settlement_id': self.id,
                        'invoice_line_ids':[(0,0,{
                            'name': self.name,
                            'quantity': 1,
                            'account_id': line.expense_account.id if line.expense_account else False,
                            'price_unit': line.commission_payable
                        })]
                    }
                    bills.create(vals)
                    for rec in line.commission_record_ids:
                        rec.commission_line.write({'state': 'bill_created'})
                self.state = 'bill_created'
            else:
                raise ValidationError('Commission Payable must be greater than Zero')

    def action_view_sale_commission(self):
        record_ids = self.env['sale.commission.record'].search([('commission_settlement', '=', self.id)]).ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Commission'),
            "views": [[self.env.ref('sd_sale_commission.sale_commission_record_view_tree').id, "tree"],
                    [[self.env.ref('sd_sale_commission.sale_commission_record_form_view').id], "form"]],
            'view_mode': 'tree,form',
            'res_model': 'sale.commission.record',
            'domain': [('id', 'in', record_ids)],
            'context':{'search_default_group_by_agent': 1}
        }

    def action_view_move(self):
        ids = self.env['account.move'].search([('settlement_id', '=', self.id)]).ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bills'),
            "views": [[self.env.ref('account.view_in_invoice_bill_tree').id, "tree"],
                    [[self.env.ref('account.view_move_form').id], "form"]],
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', ids)],
            'context':{'create': 0}
        }

class CommissionSettlementLine(models.Model):
    _name = "commission.settlement.line"
    _description = 'Commission Settlement Line'

    agent_id = fields.Many2one('sale.commission.agent', string="Agent")
    expense_account = fields.Many2one('account.account', string="Expense Account ")
    commission_payable = fields.Float(string="Commission Payable", compute="_compute_amount")
    commission_settlement_id = fields.Many2one('sale.commission.settlement')
    commission_record_ids = fields.One2many('sale.commission.record', 'settlement_line_id')

    def _compute_amount(self):
        for rec in self:
            rec.commission_payable = sum(rec.commission_record_ids.mapped('commission_amount'))
