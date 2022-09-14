# -*- coding: utf-8 -*-


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # This is a new field added on vendor form for adding discount value.
    default_supplierinfo_discount = fields.Float(
        string="Default Supplier Discount (%)",
        digits="Discount",
        help="This value will be used as the default one, for each new"
        " supplier info line depending on that supplier.",
    )
