
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        fields = fields or {}
        fields["product_brand_id"] = ", t.product_brand_id as product_brand_id"
        groupby += ", t.product_brand_id"
        return super()._query(with_clause, fields, groupby, from_clause)
