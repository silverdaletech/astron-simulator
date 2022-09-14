# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import format_amount


SALE_AGREEMENT_STATES = [
    ('new', 'New'),
    ('sent', 'Agreement Sent'),
    ('ongoing', 'Confirmed'),
    ('done', 'Closed'),
    ('cancel', 'Cancelled')
]


class SaleAgreement(models.Model):
    _name = "sale.agreement"
    _description = "Sale Agreement"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "id desc"

    name = fields.Char(string='Reference', required=True, copy=False, default='New', readonly=True)
    # origin = fields.Char(string='Source Document')
    order_count = fields.Integer(compute='_compute_orders_number', string='Number of Orders')
    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    customer_ref = fields.Char(string='Customer Reference')
    is_copy_customer_ref = fields.Boolean(string='Is Copy Customer Ref', default=True)
    date_end = fields.Datetime(string='Agreement Deadline', tracking=True)
    user_id = fields.Many2one('res.users', string='Sales Representative',
                              default=lambda self: self.env.user, check_company=True)
    description = fields.Html()
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sale_ids = fields.One2many('sale.order', 'agreement_id', string='Sale Orders', states={'done': [('readonly', True)]})
    line_ids = fields.One2many('sale.agreement.line', 'agreement_id', string='Products to Sale', states={'done': [('readonly', True)]}, copy=True)
    product_id = fields.Many2one('product.product', related='line_ids.product_id', string='Product')
    state = fields.Selection(SALE_AGREEMENT_STATES, 'Status', tracking=True, required=True,
                             copy=False, default='new')
    # state_blanket_order = fields.Selection(SALE_AGREEMENT_STATES, compute='_set_state')

    # exclusive = fields.Selection([('exclusive', 'Select only one Quotation (exclusive)'), ('multiple', 'Select multiple Quotations (non-exclusive)')],
    #                              string='Agreement Selection Type', required=True, default='multiple',
    #                              help="""Select only one Quotation (exclusive):  when a sale order is confirmed, cancel the remaining sale orders.\n
    #                                                  Select multiple Quotations (non-exclusive): allows multiple sale orders. On confirmation of a sale order it does not cancel the remaining orders""")
    is_quantity_copy = fields.Selection([('copy', 'Use quantities of agreement'), ('none', 'Set quantities manually')],
                                        string='Quantities', required=True, default='none')
    line_copy = fields.Selection([('copy', 'Use lines of agreement'), ('manual', 'Manually Select Lines for SO'), ('none', 'Do not create Sale order lines automatically')],
                                 string='Lines', required=True, default='copy')
    is_existing_agreement = fields.Boolean('Existing Agreement', compute='_validation_message', readonly=True, )
    validation_message = fields.Char(
        string='Validation Message', compute='_validation_message',
        required=False, store=True)
    totals_json = fields.Monetary(string='Total', compute='_compute_totals_json')
    planned_date_begin = fields.Datetime("Start date", tracking=True,)
    planned_date_end = fields.Datetime("End date", tracking=True,)
    
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'new': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True, ondelete="restrict")
    show_update_pricelist = fields.Boolean(string='Has Pricelist Changed',
                                           help="Technical Field, True if the pricelist was changed;\n"
                                                " this will then display a recomputation button")
    report_type_portal = fields.Selection(
        string='Portal Display', selection=[('normal', 'Sale Agreement'),
                                            ('detail', 'Sale Agreement With Details'), ], default='normal')
    is_to_invoice = fields.Boolean(compute="compute_to_invoice_status")
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string='Invoice Address',
        required=False)
    invoice_status = fields.Selection([
        ('need_action','Need Action'),
        ('invoiced','Fully Invoiced'),
        ('to_invoice','To Invoice'),
        ('no','Nothing to Invoice'),
        ],string="Invoice Status",
        compute='compute_to_invoice_status')
    
    def compute_to_invoice_status(self):
        for rec in self:
            rec.is_to_invoice = any(rec.sale_ids.filtered(lambda x: x.invoice_status == 'to invoice'))
            if any(rec.sale_ids.filtered(lambda x: x.invoice_status == 'to invoice' and x.state != 'cancel')):
                rec.invoice_status = 'to_invoice'
            elif any(rec.sale_ids.filtered(lambda x: x.invoice_status == 'no' and x.state != 'cancel')):
                rec.invoice_status = 'no'
            elif any(rec.sale_ids.filtered(lambda x: x.invoice_status == 'invoiced' and x.state != 'cancel')):
                rec.invoice_status = 'invoiced'
            else:
                rec.invoice_status = 'need_action'

    def _get_update_prices_lines(self):
        """ Hook to exclude specific lines which should not be updated based on price list recomputation """
        return self.line_ids.filtered(lambda line: not line.display_type)
    
    
    @api.onchange('pricelist_id', 'line_ids')
    def _onchange_pricelist_id(self):
        if self.line_ids and self.pricelist_id and self._origin.pricelist_id != self.pricelist_id:
            self.show_update_pricelist = True
        else:
            self.show_update_pricelist = False

    def update_prices(self):
        self.ensure_one()
        for line in self._get_update_prices_lines():
            line.product_uom_change()
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", self.pricelist_id.display_name))

    @api.depends('pricelist_id', 'planned_date_begin', 'company_id')
    def _compute_currency_rate(self):
        for order in self:
            if not order.company_id:
                order.currency_rate = order.currency_id.with_context(date=order.planned_date_begin).rate or 1.0
                continue
            elif order.company_id.currency_id and order.currency_id:  # the following crashes if any one is undefined
                order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id, order.currency_id, order.company_id, order.planned_date_begin)
            else:
                order.currency_rate = 1.0

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """

        self = self.with_company(self.company_id)
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        # if not self.env.context.get('not_self_saleperson') or not self.team_id:
        #     values['team_id'] = self.env['crm.team'].with_context(
        #         default_team_id=self.partner_id.team_id.id
        #     )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

    def preview_sale_agreement(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _get_return_portal_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('sd_sale_agreement.action_sale_agreement')

    def _compute_access_url(self):
        super(SaleAgreement, self)._compute_access_url()
        for agreement in self:
            agreement.access_url = '/my/agreement/%s' % agreement.id

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.agreement.blanket.order') or _('New')

        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)
        result = super(SaleAgreement, self).create(vals)
        return result
    
    @api.depends('line_ids', 'line_ids.price_unit', 'line_ids.product_qty')
    def _compute_totals_json(self):
        for rec in self:
            total_price = 0
            if rec.line_ids:
                total_price = sum(rec.line_ids.mapped('price_line_total'))
            rec.totals_json = total_price

    def _validation_message(self):
        agreements = self.env['sale.agreement'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', 'in', ['new', 'sent', 'ongoing']),
            ('is_quantity_copy', '=', 'none'),
            ('company_id', '=', self.company_id.id),
        ])
        message = ""
        existing = False
        is_disable_sa_warning = self.env['ir.config_parameter'].sudo().get_param(
            'sd_sale_agreement.is_disable_sa_warning')
        if len(agreements) > 1:
            if not is_disable_sa_warning:
                for agreement in agreements:
                    existing = True
                    message = "There is already a Sale Agreement for %s. We suggest you complete that Sale Agreements, instead of creating a new one." % self.partner_id.name

            self.is_existing_agreement = existing
            self.validation_message = message
        else:
            self.is_existing_agreement = False

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('sale.agreement.blanket.order') or _('New')
    #
    #     result = super(SaleAgreement, self).create(vals)
    #     return result

    @api.onchange('partner_id')
    def _onchange_customer(self):
        self = self.with_company(self.company_id)
        if not self.partner_id:
            self.currency_id = self.env.company.currency_id.id
        else:
            self.currency_id = self.partner_id.currency_id.id or self.env.company.currency_id.id

        agreements = self.env['sale.agreement'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'ongoing'),
            ('is_quantity_copy', '=', 'none'),
            ('company_id', '=', self.company_id.id),
        ])
        # if any(agreements):
        #     self.is_existing_agreement = True
        #     self.validation_message = "There is already a Sale Agreement for %s. We suggest you complete that Sale Agreements, instead of creating a new one." % self.partner_id.name
            # title = _("Warning for %s", self.partner_id.name)
            # message = _("There is already an open blanket order for this customer. We suggest you complete this open blanket order, instead of creating a new one.")
            # warning = {
            #     'title': title,
            #     'message': message
            # }
            # return {'warning': warning}
        # else:
        #     self.is_existing_agreement = False

    @api.depends('sale_ids')
    def _compute_orders_number(self):
        for agreement in self:
            agreement.order_count = len(agreement.sale_ids)

    def action_send_email(self):

        template_id = self.env['ir.model.data']._xmlid_to_res_id('sd_sale_agreement.email_template_sale_agreement', raise_if_not_found=False)

        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.agreement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'mark_agreement_as_sent': True,
        }
        if self.state == 'new':
            self.write({'state': 'sent'})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    def action_cancel(self):
        # try to set all associated quotations to cancel state
        for agreement in self:
            agreement.sale_ids.action_cancel()
            for so in agreement.sale_ids:
                so.message_post(body=_('Cancelled by the agreement associated to this quotation.'))
        self.write({'state': 'cancel'})

    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", self.name))

        for agreement in self.filtered(lambda x: x.partner_id not in x.message_partner_ids):
            agreement.message_subscribe([agreement.partner_id.id])
        if self.is_quantity_copy == 'none' and self.partner_id:
            for agreement_line in self.line_ids:
                if agreement_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the sale agreement without price.'))
                if agreement_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the sale agreement without quantity.'))
            self.write({'state': 'ongoing'})
        else:
            self.write({'state': 'ongoing'})

    def action_open(self):
        self.write({'state': 'open'})

    def action_draft(self):
        self.ensure_one()
        self.name = 'New'
        self.write({'state': 'new'})

    def action_done(self):
        """
        Generate all Sale order based on selected lines, should only be called on one agreement at a time
        """
        if any(sale_order.state in ['draft', 'sent'] for sale_order in self.mapped('sale_ids')):
            raise UserError(_('You have to cancel or validate every Quotation before closing the sale agreement.'))
        self.write({'state': 'done'})

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft_or_cancel(self):
        if any(agreement.state not in ('new', 'cancel') for agreement in self):
            raise UserError(_('You can only delete New agreements.'))

    def unlink(self):
        # Draft agreement could have some agreement lines.
        self.mapped('line_ids').unlink()
        return super(SaleAgreement, self).unlink()

    def action_confirm_wizard(self):
        self.ensure_one()
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "sale.agreement.wizard",
            # "res_id": self.id,
            "name": "Agreement Lines Selection",
            "views": [[False, "form"]],
            "context": {"create": False,
                        # "default_user_id": self.user_id.id,
                        "default_sale_agreement_id": self.id,
                        "from_sale_agreement": True,
                        },
            "target": "new",

        }
        return action_window

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        # if self.env.context.get('mark_agreement_as_sent'):
            # self.filtered(lambda o: o.state == 'draft').with_context(tracking_disable=True).write({'state': 'sent'})
        return super(SaleAgreement, self.with_context(mail_post_autofollow=self.env.context.get('mail_post_autofollow', True))).message_post(**kwargs)


class SaleAgreementLine(models.Model):
    _name = "sale.agreement.line"
    _description = "Sale Agreement Line"
    _rec_name = 'product_id'

    sequence = fields.Integer(string='Sequence', default=10)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)])
    product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_qty = fields.Float(string='Agreement Qty', tracking=True, digits='Product Unit of Measure')
    product_description_variants = fields.Char('Custom Description')
    price_unit = fields.Float(string='Unit Price', tracking=True, digits='Product Price')
    qty_ordered = fields.Float(compute='_compute_ordered_qty', string='Ordered Qty')
    qty_invoiced = fields.Float(compute='_compute_ordered_qty', string='Invoiced Qty')
    qty_delivered = fields.Float(compute='_compute_ordered_qty', string='Delivered Qty')
    agreement_id = fields.Many2one('sale.agreement', string='Sale Agreement', ondelete='cascade')
    date_deadline = fields.Datetime(string='Date Deadline', related='agreement_id.date_end')
    company_id = fields.Many2one('res.company', related='agreement_id.company_id', string='Company', store=True, readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', compute="_compute_analytic_account_id", store=True, readonly=False, check_company=True, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', compute="_compute_analytic_tag_ids", store=True, readonly=False, check_company=True, copy=True)
    sale_order_line = fields.One2many('sale.order.line', 'sale_agreement_line', string='Sale Order Line')
    price_line_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    take_to_sale_rfq = fields.Boolean(string='Take to Sale Rfq')
    line_copy = fields.Selection([('copy', 'Use lines of agreement'), ('manual', 'Manually Select Lines for SO'), ('none', 'Do not create Sale order lines automatically')],
                                 string='Lines', related='agreement_id.line_copy', default='copy')
    is_sale_line_for_wizard = fields.Boolean(string='Take to Sale Rfq')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values", ondelete='restrict')

    @api.depends('product_id', 'agreement_id.partner_id')
    def _compute_analytic_account_id(self):
        for record in self:
            rec = self.env['account.analytic.default'].account_get(
                product_id=record.product_id.id,
                partner_id=record.agreement_id.partner_id.commercial_partner_id.id,
                # account_id=record.account_id.id,
                user_id=record.env.uid,
                date=record.date_deadline.date() if record.date_deadline else False,
                company_id=record.agreement_id.company_id.id
            )
            if rec:
                record.account_analytic_id = rec.analytic_id
            else:
                record.account_analytic_id = False

    @api.depends('product_id', 'agreement_id.partner_id')
    def _compute_analytic_tag_ids(self):
        for record in self:
            rec = self.env['account.analytic.default'].account_get(
                product_id=record.product_id.id,
                partner_id=record.agreement_id.partner_id.commercial_partner_id.id,
                # account_id=record.account_id.id,
                user_id=record.env.uid,
                date=record.date_deadline.date() if record.date_deadline else False,
                company_id=record.agreement_id.company_id.id
            )
            if rec:
                record.analytic_tag_ids = rec.analytic_tag_ids
            else:
                record.analytic_tag_ids = False

    @api.onchange('take_to_sale_rfq')
    def _onchange_take_to_sale_rfq(self):
        for line in self:
            line.is_sale_line_for_wizard = line.take_to_sale_rfq

    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        lin_total = 0
        for rec in self:
            line_total = rec.product_qty * rec.price_unit
            rec.price_line_total = line_total

    @api.model
    def create(self, vals):
        res = super(SaleAgreementLine, self).create(vals)
        if res.agreement_id.state not in ['new', 'cancel', 'done'] and res.agreement_id.is_quantity_copy == 'none':
            if vals['price_unit'] <= 0.0:
                raise UserError(_('You cannot confirm the sale agreement without price.'))
        return res

    def write(self, vals):
        res = super(SaleAgreementLine, self).write(vals)
        if 'price_unit' in vals:
            if vals['price_unit'] <= 0.0 and any(
                    agreement.state not in ['new', 'cancel', 'done'] and
                    agreement.is_quantity_copy == 'none' for agreement in self.mapped('agreement_id')):
                raise UserError(_('You cannot confirm the sale agreement without price.'))

        return res

    @api.depends('agreement_id.sale_ids.state')
    def _compute_ordered_qty(self):
        line_found = set()
        for line in self:
            total = 0.0
            total_invoiced = 0.0
            total_delivered = 0.0
            for so in line.agreement_id.sale_ids.filtered(lambda sale_order: sale_order.state in ['sale', 'done']):
                for so_line in so.order_line.filtered(lambda order_line: order_line.product_id == line.product_id):
                    if so_line.product_uom != line.product_uom_id:
                        total += so_line.product_uom._compute_quantity(so_line.product_uom_qty, line.product_uom_id)
                    else:
                        total += so_line.product_uom_qty
                    if so_line.qty_delivered:
                        total_delivered += so_line.qty_delivered

                    if so_line.qty_invoiced:
                        total_invoiced += so_line.qty_invoiced

            if line.product_id not in line_found:
                line.qty_ordered = total
                line_found.add(line.product_id)
            else:
                line.qty_ordered = 0
            line.qty_delivered = total_delivered
            line.qty_invoiced = total_invoiced

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            self.product_qty = 1.0

    def _prepare_sale_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        agreement = self.agreement_id
        if self.product_description_variants:
            name += '\n' + self.product_description_variants
        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': product_qty,
            'price_unit': price_unit,
            'tax_id': [(6, 0, taxes_ids)],
            'analytic_tag_ids': self.analytic_tag_ids.ids,
            'sale_agreement_line': self.id,
        }




    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )

        if self.agreement_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.agreement_id.pricelist_id.id, uom=self.product_uom_id.id).price
        product_context = dict(self.env.context, partner_id=self.agreement_id.partner_id.id, date=self.agreement_id.planned_date_begin, uom=self.product_uom_id.id)

        final_price, rule_id = self.agreement_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_qty or 1.0, self.agreement_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_qty, self.product_uom_id, self.agreement_id.pricelist_id.id)
        if currency != self.agreement_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.agreement_id.pricelist_id.currency_id,
                self.agreement_id.company_id or self.env.company, self.agreement_id.planned_date_begin or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    
    @api.onchange('product_uom_id', 'product_qty')
    def product_uom_change(self):
        if not self.product_uom_id or not self.product_id:
            self.price_unit = 0.0
            return
        if self.agreement_id.pricelist_id and self.agreement_id.partner_id:
            product = self.product_id.with_context(
                lang=self.agreement_id.partner_id.lang,
                partner=self.agreement_id.partner_id,
                quantity=self.product_qty,
                date=self.agreement_id.planned_date_begin,
                pricelist=self.agreement_id.pricelist_id.id,
                uom=self.product_uom_id.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = product._get_tax_included_unit_price(
                self.company_id or self.agreement_id.company_id,
                self.agreement_id.currency_id,
                self.agreement_id.planned_date_begin,
                'sale',
                fiscal_position=False,
                product_price_unit=self._get_display_price(product),
                product_currency=self.agreement_id.currency_id
            )

    
    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    _price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.agreement_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.company, self.agreement_id.planned_date_begin or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    
    @api.onchange('product_id', 'price_unit', 'product_uom_id', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom_id and
                self.agreement_id.partner_id and self.agreement_id.pricelist_id and
                self.agreement_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.agreement_id.partner_id.lang,
            partner=self.agreement_id.partner_id,
            quantity=self.product_qty,
            date=self.agreement_id.planned_date_begin,
            pricelist=self.agreement_id.pricelist_id.id,
            uom=self.product_uom_id.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.agreement_id.partner_id.id, date=self.agreement_id.planned_date_begin, uom=self.product_uom_id.id)

        price, rule_id = self.agreement_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_qty or 1.0, self.agreement_id.partner_id)
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_qty, self.product_uom_id  , self.agreement_id.pricelist_id.id)

        if new_list_price != 0:
            if self.agreement_id.pricelist_id.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, self.agreement_id.pricelist_id.currency_id,
                    self.agreement_id.company_id or self.env.company, self.agreement_id.planned_date_begin or fields.Date.today())
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                self.discount = discount

    def _is_delivery(self):
        self.ensure_one()
        return False


    def _is_not_sellable_line(self):
        # True if the line is a computed line (reward, delivery, ...) that user cannot add manually
        return False