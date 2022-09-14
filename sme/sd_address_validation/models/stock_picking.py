from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_type = fields.Selection(
        string='Stock_type',related='picking_type_id.code',store=True,
        required=False, )
        

    def button_validate_partner_address(self):
        for order in self:
            if order and order.partner_id:
                return order.partner_id.button_validate_address()
