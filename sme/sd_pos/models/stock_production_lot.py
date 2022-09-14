# -*- coding: utf-8 -*-


from odoo import _, api, fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def get_product_lots(self, product):
        lots_details = []
        if product:
            lot_ids = self.sudo().search([('product_id', '=', product)])
            for lot in lot_ids:
                lots_details.append({'text': lot.name})
        return lots_details
