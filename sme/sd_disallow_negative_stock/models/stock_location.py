# -*- coding: utf-8 -*-

from odoo import fields, models


class StockLocation(models.Model):
     _inherit = "stock.location"
     prevent_negative_stock = fields.Boolean(string="Prevent Negative Inventory",
                                        help="Prevent negative inventory levels for the stockable products "
                                        "attached to this location.",
                                        )
