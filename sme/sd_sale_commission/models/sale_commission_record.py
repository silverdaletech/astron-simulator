# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SaleCommissionRecord(models.Model):
    _name = 'sale.commission.record'
    _description = 'Sale Commission Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Name', tracking=True)
    commission_agent = fields.Many2one('sale.commission.agent' ,string='Commission Agent', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Related Contact', tracking=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", tracking=True)
    commission_expense_acc_id = fields.Many2one('account.account', string='Commission Expense Account', tracking=True)
    commission_line = fields.One2many('sale.commission.line', 'commission_record_id', readonly=False, tracking=True)
    commission_settlement = fields.Many2one('sale.commission.settlement', tracking=True)
    
    total_invoice_amount = fields.Monetary(stirng="Total Invoice Amount", tracking=True)
    commissionable_amount = fields.Monetary(stirng="Commissionable Amount", compute='_compute_amount', tracking=True)
    commission_amount = fields.Monetary(stirng="Commission Amount", compute='_compute_amount', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  default=lambda self: self.env.company.currency_id.id, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, tracking=True,
                                 default=lambda self: self.env.company)
    settlement_line_id = fields.Many2one('commission.settlement.line', ondelete='cascade')
    state = fields.Selection([
                        ('pending', 'Pending'),
                        ('bill_created', 'Bill Created'),
                        ],default='pending', tracking=True)

    def _compute_amount(self):
        for rec in self:
            rec.commissionable_amount = sum(rec.commission_line.mapped('commissionable_amount'))
            rec.commission_amount = sum(rec.commission_line.mapped('commission_amount'))

class SaleCommissionLine(models.Model):
    _name = 'sale.commission.line'

    name = fields.Char(string="Description")
    product_id = fields.Many2one('product.product',string="Product")
    unit_price = fields.Float(string="Unit Price")
    qty = fields.Float(stirng="Quantity")
    # uom_id = fields.Many2one('',stirng="UOM")
    subtotal = fields.Monetary(stirng="Subtotal")
    commissionable_amount = fields.Monetary(stirng="Commissionable Amount")
    commission_amount = fields.Monetary(stirng="Commission Amount")
    commission_record_id = fields.Many2one('sale.commission.record',ondelete='cascade')
    move_line_id = fields.Many2one('account.move.line')
    agent_id = fields.Many2one('sale.commission.agent')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                default=lambda self: self.env.company.currency_id.id, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, tracking=True,
                                    default=lambda self: self.env.company)
    state = fields.Selection([
                            ('pending', 'Pending'),
                            ('bill_created', 'Bill Created'),
                            ],default='pending', readonly=True,
                            stirng="Settlement Status")
