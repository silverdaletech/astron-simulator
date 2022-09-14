from odoo import models, api, fields, _ 


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    vendor_lot_num = fields.Char(string='Vendor Lot Number')
