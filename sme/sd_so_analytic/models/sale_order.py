from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    def _prepare_invoice_line(self, **optional_values):
        """This function will send account analytic to invoice lines"""

        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.analytic_account_id:
            res['analytic_account_id'] = self.analytic_account_id.id
        return res

    @api.onchange('product_id')
    def _set_analytic_account(self):
        """This will set defaults analytic account on order line"""
        analytic_account_id = False
        if self.product_id:
            account_analytic_default = self.env['account.analytic.default'].account_get(
                partner_id=self.order_id.partner_id.commercial_partner_id.id,
                user_id=self.order_id.user_id.id,
                company_id=self.company_id.id,
                product_id=self.product_id.id,
                warehouse_id=self.order_id.warehouse_id.id
            )
            self.analytic_account_id = account_analytic_default.analytic_id.id or False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('warehouse_id')
    def _set_analytic_account(self):
        """This will set default analytic account on sale order"""
        analytic_account_id = False
        if self.warehouse_id:
            account_analytic_default = self.env['account.analytic.default'].account_get(
                partner_id=self.partner_id.commercial_partner_id.id,
                company_id=self.company_id.id,
                user_id=self.user_id.id,
                warehouse_id=self.warehouse_id.id
            )
            self.analytic_account_id = account_analytic_default.analytic_id.id or False
