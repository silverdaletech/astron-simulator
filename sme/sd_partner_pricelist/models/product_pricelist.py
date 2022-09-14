# -*- coding: utf-8 -*-
from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def show_pricelist_partners(self):
        if len(self) == 1:
            domain = [("property_product_pricelist", "=", self.id)]
        else:
            domain = [("property_product_pricelist", "in", self.ids)]
        partners = self.env["res.partner"].search(domain)
        action = self.env.ref("base.action_partner_form")
        res = action.read()[0]
        res["domain"] = [
            ("id", "in", partners.ids),
        ]
        return res