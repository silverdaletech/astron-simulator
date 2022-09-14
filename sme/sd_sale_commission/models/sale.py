# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_agent_id = fields.Many2one('sale.commission.agent',
                                          string='Commission Agent', related='partner_id.commission_agent_id',readonly=False)
    mandatory = fields.Boolean(
        string='Mandatory',default=False)

    @api.depends('order_line')
    @api.onchange('order_line')
    def onchange_method(self):
        if any(line.product_id.commissionable == True for line in self.order_line):
            self.mandatory =True
        else:
            self.mandatory= False
        # if any(line.delivery_status == 'pending' for line in order.order_line if line.product_id.type in product_types):

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['sale_commission_id'] =self.commission_agent_id.id if self.commission_agent_id else False
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res['commissionable_line'] = self.product_id.commissionable
        return res