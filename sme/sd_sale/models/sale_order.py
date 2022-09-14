from odoo import models, fields, api, _
import json


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    allow_price_change = fields.Boolean(
        string='Allow Price change in SO', default=True,
        required=False)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    compute_can_edit_price = fields.Boolean(
        compute="compute_compute_can_edit_price", )
    partner_shipping_id_domain = fields.Char(compute="_compute_partner_child_ids_domain", readonly=True, store=False)
    partner_invoice_id_domain = fields.Char(compute="_compute_partner_child_ids_domain", readonly=True, store=False)

    # Below method is used to compute dynamic domain for various fields on sale order.
    @api.depends('partner_id')
    def _compute_partner_child_ids_domain(self):
        for rec in self:
            domain = [('company_id', 'in', [False, rec.company_id.id])]
            if rec.partner_id:
                if rec.partner_id.company_type == 'company':
                    ids = rec.partner_id.child_ids.ids
                    ids.append(rec.partner_id.id)
                    domain = [('company_id', 'in', [False, rec.company_id.id]), ('id', 'in', ids)]
                else:
                    if rec.partner_id.parent_id:
                        other_ids = rec.partner_id.parent_id.child_ids.ids
                        other_ids.append(rec.partner_id.parent_id.id)
                        domain = [('company_id', 'in', [False, rec.company_id.id]), ('id', 'in', other_ids)]
                    else:
                        domain = [('company_id', 'in', [False, rec.company_id.id]), ('id', '=', rec.partner_id.id)]

            rec.partner_shipping_id_domain = json.dumps(domain)
            rec.partner_invoice_id_domain = json.dumps(domain)

    def compute_compute_can_edit_price(self):
        self.compute_can_edit_price = False
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        if user.has_group('sd_sale.group_sale_order_price_change'):
            self.compute_can_edit_price = True
        self.order_line._compute_can_edit_price()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    can_edit_price = fields.Boolean(
        compute="_compute_can_edit_price",
        store=True)

    @api.depends('product_id', 'order_id', 'order_id.sale_order_template_id', 'order_id.compute_can_edit_price')
    @api.onchange('order_id.compute_can_edit_price')
    def _compute_can_edit_price(self):
        for rec in self:
            rec.can_edit_price = True
            if self.env['ir.config_parameter'].sudo().get_param('sd_sale.sale_price_change'):
                context = self._context
                current_uid = context.get('uid')
                user = self.env['res.users'].browse(current_uid)
                if rec.order_id and rec.order_id.sale_order_template_id:
                    if not rec.order_id.sale_order_template_id.allow_price_change:
                        if rec.product_id in rec.order_id.sale_order_template_id.sale_order_template_line_ids.mapped(
                                'product_id'):
                            if user.has_group('sd_sale.group_sale_order_price_change'):
                                rec.can_edit_price = True
                            elif rec.price_unit == 0:
                                rec.can_edit_price = True
                            else:
                                rec.can_edit_price = False
