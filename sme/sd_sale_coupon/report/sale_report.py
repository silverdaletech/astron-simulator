# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleReport(models.Model):
    _inherit = "sale.report"

    promotional_discount = fields.Float(string='Promotional Discount', readonly=True)
    discounted_total = fields.Float(string='Discounted Total', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """
        Include promotional_discount and discounted_total in the query in order for these fields to appear in measures.
        """
        fields['promotional_discount'] = ", l.promotional_discount as promotional_discount"
        fields['discounted_total'] = ", l.discounted_total as discounted_total"
        groupby += ', l.promotional_discount'
        groupby += ', l.discounted_total'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
