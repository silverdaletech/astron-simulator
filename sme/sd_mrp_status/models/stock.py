# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        """
        In order to link manufacturing order with its sale line uniquely, propagate sale order line id to _prepare_mo_vals method.
        """
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin,
                                                      company_id, values, bom)
        if values.get('sale_line_id', False):
            res.update({
                'sale_line_id': values.get('sale_line_id', False),
            })
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        """
        In order to link manufacturing order with its sale line uniquely, propagate sale order line id to _prepare_procurement_values method.
        """
        res = super(StockMove, self)._prepare_procurement_values()
        if self.sale_line_id.id:
            res.update({
                'sale_line_id': self.sale_line_id.id,
            })
        return res

