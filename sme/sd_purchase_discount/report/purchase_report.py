# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    discount = fields.Float(
        string="Discount (%)", digits="Discount", group_operator="avg"
    )

    def _select(self):
        res = super()._select()
        # There are 3 matches
        res = res.replace("l.price_unit", self._get_discounted_price_unit_exp())
        res += ", l.discount AS discount"
        return res

    def _group_by(self):
        res = super()._group_by()
        res += ", l.discount"
        return res

    def _get_discounted_price_unit_exp(self):
        """Inheritable method for getting the SQL expression used for
        calculating the unit price with discount(s).

        :rtype: str
        :return: SQL expression for discounted unit price.
        """
        return "(1.0 - COALESCE(l.discount, 0.0) / 100.0) * l.price_unit"
