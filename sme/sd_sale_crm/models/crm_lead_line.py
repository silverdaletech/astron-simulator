# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CrmLeadLine(models.Model):
    _name = "crm.lead.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Line in CRM Lead"

    
    lead_id = fields.Many2one("crm.lead", string="Lead")
    name = fields.Char("Description", required=True, translate=True, tracking=True)
    product_id = fields.Many2one("product.product", string="Product", index=True, tracking=True)
    category_id = fields.Many2one(
        "product.category", string="Product Category", index=True, tracking=True
    )
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", index=True, tracking=True
    )
    product_barcode = fields.Char(
        string="Barcode",
        related="product_id.barcode",
        store=True)
    product_qty = fields.Integer(string="Product Quantity", default=1, required=True, tracking=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", readonly=True, tracking=True)
    price_unit = fields.Float(string="Price Unit", readonly="1", tracking=True)
    price_offered = fields.Float(string="Offered Price", tracking=True)
    percentage_difference = fields.Float(string="Percentage Difference", 
        compute="_compute_amount", tracking=True,
        store=True)
    planned_revenue = fields.Float(
        compute="_compute_planned_revenue",
        string="Planned revenue",
        store=True,
        tracking=True,
    )
    expected_revenue = fields.Float(
        compute="_compute_expected_revenue",
        string="Expected revenue",
        store=True,
        tracking=True,
    )
    estimated_revenue = fields.Float(
        string="Estimated Revenue",
        compute="_compute_amount",
        store=True,
        tracking=True,
    )
    actual_revenue = fields.Float(string="Actual Revenue",
        compute="_compute_actual_qty_sold",
        store= True,
        tracking=True,
    )
    actual_qty_sold = fields.Float(
        string="Actual Qty Sold", 
        compute="_compute_actual_qty_sold",
        store= True,
        tracking=True,
    )
    sale_type = fields.Selection([
                ('planned', 'Planned Revenue'),
                ('unexpected', 'Unexpected Revenue'),
            ], default='planned', required=True, tracking=True)
    
    company_id = fields.Many2one(related='lead_id.company_id')
    
    can_edit_offer = fields.Boolean(
        compute="_compute_can_edit_offer_price",
        store=True
    )
    allow_percentage = fields.Float(compute="_compute_can_edit_offer_price")

    sale_line_ids = fields.One2many('sale.order.line', 'crm_lead_line_id')
    
    #------------------------------------------------
    # Computed Fields
    #------------------------------------------------

    @api.depends("price_unit", "product_qty")
    def _compute_planned_revenue(self):
        for rec in self:
            rec.planned_revenue = rec.product_qty * rec.price_unit

    @api.depends("lead_id.probability", "planned_revenue")
    def _compute_expected_revenue(self):
        for rec in self:
            if rec.lead_id and rec.lead_id.type != "lead":
                rec.expected_revenue = (
                    rec.planned_revenue * rec.lead_id.probability * (1 / 100)
                )

    @api.depends("price_unit", "price_offered", "product_qty", "lead_id.probability")
    def _compute_amount(self):
        for rec in self:
            if rec.price_unit != 0:
                rec.percentage_difference = ((rec.price_unit - rec.price_offered) / rec.price_unit ) * 100
            else:
                rec.percentage_difference = 0
            rec.expected_revenue = rec.price_offered * rec.product_qty
            rec.estimated_revenue = rec.expected_revenue * (rec.lead_id.probability/100)

    def _compute_can_edit_offer_price(self):
        for rec in self:
            can_edit = False
            rec.allow_percentage = 0
            if rec.company_id.crm_product_price_rule == 'roles':
                groups = self.env['crm.price.role'].search([], order='allow_percentage desc')
                for group in groups:
                    if group.name.id in self.env.user.groups_id.ids:
                        can_edit = True
                        rec.allow_percentage = group.allow_percentage
                        break
            elif rec.company_id.crm_product_price_rule == 'team':
                member = self.env['crm.team.member'].search([
                    ('user_id', '=', rec.env.user.id),
                    ('allow_offer', '=', True)
                ], limit=1)
                if member:
                    can_edit = True
                    rec.allow_percentage = member.allow_percentage
            else:
                can_edit = True
            rec.can_edit_offer = can_edit

    @api.depends('sale_line_ids','sale_line_ids.state')
    @api.onchange('sale_line_ids','sale_line_ids.state')
    def _compute_actual_qty_sold(self):
        for rec in self:
            rec.actual_qty_sold  = sum(rec.sale_line_ids.filtered(lambda x: x.state in ('sale', 'done')).mapped('product_uom_qty'))
            rec.actual_revenue = sum(rec.sale_line_ids.filtered(lambda x: x.state in ('sale', 'done')).mapped('price_subtotal'))
    
    #----------------------------------------------------
    # Onchange api
    #----------------------------------------------------

    @api.onchange("product_id")
    def _onchange_product_id(self):
        domain = {}
        if not self.lead_id:
            return

        if not self.product_id:
            self.price_unit = 0.0
            domain["uom_id"] = []
            if self.name and self.name != self.category_id.name:
                self.name = ""
        else:
            product = self.product_id
            self.category_id = product.categ_id.id
            self.product_tmpl_id = product.product_tmpl_id.id
            self.price_unit = product.list_price

            if product.name:
                self.name = product.name

            if (
                not self.uom_id
                or product.uom_id.category_id.id != self.uom_id.category_id.id
            ):
                self.uom_id = product.uom_id.id
            domain["uom_id"] = [("category_id", "=", product.uom_id.category_id.id)]

            if self.uom_id and self.uom_id.id != product.uom_id.id:
                self.price_unit = product.uom_id._compute_price(
                    self.price_unit, self.uom_id
                )
        self.price_offered = self.price_unit
        return {"domain": domain}

    @api.onchange("category_id")
    def _onchange_category_id(self):
        domain = {}
        if not self.lead_id:
            return
        if self.category_id:
            categ_id = self.category_id
            if categ_id.name and not self.name:
                self.name = categ_id.name

            # Check if there are already defined product and product template
            # and remove them if categories do not match
            if self.product_id and self.product_id.categ_id != categ_id:
                self.product_id = None
                self.name = categ_id.name
            if self.product_tmpl_id and self.product_tmpl_id.categ_id != categ_id:
                self.product_tmpl_id = None

        return {"domain": domain}

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        domain = {}
        if not self.lead_id:
            return
        if self.product_tmpl_id:
            product_tmpl = self.product_tmpl_id
            if product_tmpl.name and not self.name:
                self.name = product_tmpl.name
            self.category_id = product_tmpl.categ_id

            if self.product_id:
                # Check if there are already defined product and remove
                # if it does not match
                if self.product_id.product_tmpl_id != product_tmpl:
                    self.product_id = None
                    self.name = product_tmpl.name

        return {"domain": domain}

    @api.onchange("uom_id")
    def _onchange_uom_id(self):
        result = {}
        if not self.uom_id:
            self.price_unit = 0.0

        if self.product_id and self.uom_id:
            price_unit = self.product_id.list_price
            self.price_unit = self.product_id.uom_id._compute_price(
                price_unit, self.uom_id
            )
        self.price_offered = self.price_unit
        return result

    @api.depends('percentage_difference')
    @api.onchange('percentage_difference')
    def _onchange_percentage_difference(self):
        for rec in self:
            if abs(rec.percentage_difference) > abs(rec.allow_percentage):
                raise ValidationError(_('You are only allowed to grant a maximum of +- %s %%.'%(rec.allow_percentage)))
