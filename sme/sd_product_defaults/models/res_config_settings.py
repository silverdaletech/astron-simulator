# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    """
        model 'res.config.settings' is inherited and added 4 related boolean fields, to make barcode and reference 
        auto generated on product creation.
    """
    create_product_internal_reference = fields.Boolean(
        string="Create Product Internal Reference Automatically?",
        related='company_id.create_product_internal_reference',
        readonly=False)
    use_internal_reference_as_barcode = fields.Boolean(
        string="Use Auto-Created Internal Reference as Barcode?",
        related='company_id.use_internal_reference_as_barcode',
        readonly=False)
    is_reference_as_barcode = fields.Boolean(related='company_id.is_reference_as_barcode')
    create_product_barcode = fields.Boolean(
        string="Create Product Barcode Automatically?",
        related='company_id.create_product_barcode',
        readonly=False)

    product_template_reference_sequence = fields.Many2one('ir.sequence',
        related='company_id.product_template_reference_sequence',)
    product_template_barcode_sequence = fields.Many2one('ir.sequence',
        related='company_id.product_template_barcode_sequence',)

    product_product_reference_sequence = fields.Many2one('ir.sequence',
        related='company_id.product_product_reference_sequence',)
    product_product_barcode_sequence = fields.Many2one('ir.sequence',
        related='company_id.product_product_barcode_sequence')


class ResCompany(models.Model):
    _inherit = 'res.company'
    """
        model 'res.company' is inherited and added 3 boolean fields, to make barcode and reference auto 
        generated on product creation.
    """
    create_product_internal_reference = fields.Boolean(
        string="Create Product Internal Reference Automatically?")
    use_internal_reference_as_barcode = fields.Boolean(
        string="Use Auto-Created Internal Reference as Barcode?")
    is_reference_as_barcode = fields.Boolean(compute='_compute_is_reference_as_barcode')
    create_product_barcode = fields.Boolean(
        string='Create Product Barcode Automatically?')

    product_template_reference_sequence = fields.Many2one('ir.sequence',
                                                          compute='_compute_product_template_reference_sequence')
    product_template_barcode_sequence = fields.Many2one('ir.sequence',
                                                          compute='_compute_product_template_barcode_sequence' )

    product_product_reference_sequence = fields.Many2one('ir.sequence',
                                                          compute='_compute_product_product_reference_sequence')
    product_product_barcode_sequence = fields.Many2one('ir.sequence',
                                                          compute='_compute_product_product_barcode_sequence')


    @api.depends('use_internal_reference_as_barcode')
    def _compute_is_reference_as_barcode(self):
        for rec in self:
            if rec.use_internal_reference_as_barcode:
                rec.is_reference_as_barcode = False
                rec.create_product_barcode = False
            else:
                rec.is_reference_as_barcode = True

    def _compute_product_template_reference_sequence(self):
        for rec in self:
            seq = self.env['ir.sequence'].search([('code', '=', 'product_template.reference')], limit=1)
            if seq:
                rec.product_template_reference_sequence = seq.id

    def _compute_product_template_barcode_sequence(self):
        for rec in self:
            seq = self.env['ir.sequence'].search([('code', '=', 'product_template.barcode')], limit=1)
            if seq:
                rec.product_template_barcode_sequence = seq.id

    def _compute_product_product_reference_sequence(self):
        for rec in self:
            seq = self.env['ir.sequence'].search([('code', '=', 'product_product.reference')], limit=1)
            if seq:
                rec.product_product_reference_sequence = seq.id

    def _compute_product_product_barcode_sequence(self):
        for rec in self:
            seq = self.env['ir.sequence'].search([('code', '=', 'product_product.barcode')], limit=1)
            if seq:
                rec.product_product_barcode_sequence = seq.id

