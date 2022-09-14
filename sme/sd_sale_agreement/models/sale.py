# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_id = fields.Many2one('sale.agreement', string='Sale Agreement', copy=False)
    is_quantity_copy = fields.Selection(related='agreement_id.is_quantity_copy', readonly=False)

    @api.onchange('agreement_id', 'partner_id')
    def _onchange_agreement_id(self):
        if not self.agreement_id:
            return

        self = self.with_company(self.company_id)
        agreement = self.agreement_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = agreement.partner_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        self.partner_id = partner.id
        self.partner_invoice_id = agreement.partner_invoice_id.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = agreement.company_id.id
        self.currency_id = agreement.currency_id.id
        if agreement.is_copy_customer_ref:
            self.client_order_ref = agreement.customer_ref
        self.pricelist_id = agreement.pricelist_id
        if not self.origin or agreement.name not in self.origin.split(', '):
            if self.origin:
                if agreement.name:
                    self.origin = self.origin + ', ' + agreement.name
            else:
                self.origin = agreement.name
        self.note = agreement.description
        self.date_order = fields.Datetime.now()

        if agreement.line_copy == 'none':
            return
        elif agreement.line_copy == 'manual':
            # lines = self.order_line
            order_lines = self._context.get('order_lines')
            from_sale_agreement = self._context.get('from_sale_agreement')
            if order_lines:
                lines = agreement.line_ids.filtered(lambda l: l.id in self._context.get('order_lines'))
            elif not order_lines and from_sale_agreement:
                lines = []
            else:
                lines = agreement.line_ids
        else:
            lines = agreement.line_ids

        # Create SO lines if necessary
        order_lines = []
        for line in lines:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_sale:
                name += '\n' + product_lang.description_sale

            # Compute taxes
            taxes_ids = fpos.map_tax(line.product_id.taxes_id.filtered(lambda tax: tax.company_id == agreement.company_id)).ids

            # Compute quantity and price_unit
            # if line.product_uom_id != line.product_id.uom_id:
            #     product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_id)
            #     price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_id)
            # else:

            # if agreement.line_copy == 'manual':
            #     product_qty = line.product_uom_qty
            # else:
            product_qty = line.product_qty

            price_unit = line.price_unit

            if agreement.is_quantity_copy != 'copy':
                product_qty = 0

            # Create SO line
            order_line_values = line._prepare_sale_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
        self.order_line = [(5,0,0)]
        self.order_line = order_lines

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for so in self:
            if not so.agreement_id:
                continue
            # if so.agreement_id.exclusive == 'exclusive':
            #     others_so = so.agreement_id.mapped('sale_ids').filtered(lambda r: r.id != so.id)
            #     others_so.action_cancel()
            #     if so.state not in ['draft', 'sent']:
            #         so.agreement_id.action_done()
        return res

    @api.model
    def create(self, vals):
        sale = super(SaleOrder, self).create(vals)
        if sale.agreement_id and sale.agreement_id.partner_invoice_id:
            sale.partner_invoice_id = sale.agreement_id.partner_invoice_id.id
        return sale
    #
    # def write(self, vals):
    #     result = super(SaleOrder, self).write(vals)
    #     if vals.get('agreement_id'):
    #         self.message_post_with_view('mail.message_origin_link',
    #                 values={'self': self, 'origin': self.agreement_id, 'edit': True},
    #                 subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'))
    #     return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_agreement_line = fields.Many2one('sale.agreement.line', string='Sale Agreement Line')

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.agreement_id:
            agreement_line = self.order_id.agreement_id.line_ids.filtered(lambda order_line: order_line.product_id == self.product_id)
            if agreement_line:
                self.price_unit = agreement_line[0].price_unit

        else:
            return super(SaleOrderLine, self).product_uom_change()
