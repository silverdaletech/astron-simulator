from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    equipment_ids =fields.One2many('maintenance.equipment', 'stock_move_id')
    is_equipment_created = fields.Boolean(string="Equipment Created")