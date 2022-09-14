import math
from operator import itemgetter
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleAgreementWizard(models.TransientModel):
    _name = 'sale.agreement.wizard'
    _description = 'Sale Agreement Lines wizard'

    sale_agreement_id = fields.Many2one('sale.agreement', string='Sale Agreement',)
    line_ids = fields.Many2many('sale.agreement.line', string='Products to Sale')

    @api.onchange('sale_agreement_id')
    def _onchange_agreement_id(self):
        if not self.sale_agreement_id:
            return

        # self = self.with_company(self.company_id)
        agreement = self.sale_agreement_id
        # Create Agreement lines
        self.line_ids = agreement.line_ids.ids

    def action_create_saleorder(self):
        self.ensure_one()
        order_lines = []
        for line in self.line_ids.filtered(lambda x: x.is_sale_line_for_wizard):
            order_lines.append(line.id)

        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "name": "Agreement Lines Selection",
            "views": [[False, "form"]],
            "context": {
                        "default_agreement_id": self.sale_agreement_id.id,
                        "order_lines": order_lines,
                        },
            "target": "current",
        }

        for l in self.sale_agreement_id.line_ids:
            l.is_sale_line_for_wizard = l.take_to_sale_rfq

        return action_window


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    @api.model
    def _count(self):
        if self.env.context.get('active_model') == 'sale.agreement':
            return self.env['sale.order'].search_count([('agreement_id', '=', self.env.context.get('active_ids', []))])

        return len(self._context.get('active_ids', []))
    
    @api.model
    def _default_has_down_payment(self):
        if self._context.get('active_model') == 'sale.order' and self._context.get('active_id', False):
            sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
            return sale_order.order_line.filtered(
                lambda sale_order_line: sale_order_line.is_downpayment
            )
    
        if self._context.get('active_model') == 'sale.agreement':
            sale_order = self.env['sale.order'].search([('agreement_id', '=', self.env.context.get('active_ids', []))])
            return sale_order.order_line.filtered(
                lambda sale_order_line: sale_order_line.is_downpayment
            )

        return False

    @api.model
    def _default_currency_id(self):
        if self._context.get('active_model') == 'sale.order' and self._context.get('active_id', False):
            sale_order = self.env['sale.order'].browse(self._context.get('active_id'))

        if self._context.get('active_model') == 'sale.agreement':
            sale_order = self.env['sale.order'].search([('agreement_id', '=', self.env.context.get('active_ids', []))])

    deduct_down_payments = fields.Boolean('Deduct down payments', default=True)
    has_down_payments = fields.Boolean('Has down payments', default=_default_has_down_payment, readonly=True)
    count = fields.Integer(default=_count, string='Order Count')

    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency_id)

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        
        if self.env.context.get('active_model') == 'sale.agreement':
            sale_orders =  self.env['sale.order'].search([('agreement_id', '=', self.env.context.get('active_ids', []))])

        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                so_line = sale_line_obj.create(so_line_values)
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
