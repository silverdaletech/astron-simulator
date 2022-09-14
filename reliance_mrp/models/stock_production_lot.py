from odoo import models, api, fields, _ 


class StockProductLot(models.Model):
    _inherit = 'stock.production.lot'

    vendor_lot_num = fields.Char(string='Vendor Lot Number')