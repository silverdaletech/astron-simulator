# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    """
    res.partner model is inherited to add following field and display a page on contact form view
    """
    _inherit = 'product.product'

    @api.onchange('categ_id')
    def category_onchange(self):
        if self.categ_id:
            self.commissionable = self.categ_id.commissionable

    def category_default(self):
        return self.categ_id.commissionable

    commissionable= fields.Boolean(string='Commission-able?', default=category_default)


class ProductCategory(models.Model):
    """
    res.partner model is inherited to add following field and display a page on contact form view
    """
    _inherit = 'product.category'

    commissionable= fields.Boolean(string='Commission-able?')

    @api.depends('commissionable')
    @api.onchange('commissionable')
    def onchange_method(self):
        product = self.env['product.product'].search([('categ_id', '=', self.ids)])
        if product:
            product.write({
                'commissionable': self.commissionable
            })
