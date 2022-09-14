from odoo import fields, api, models, _ 


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lot_prefix = fields.Selection(string="Lot Number Prefix",
        selection=[
            ('P', 'Powder'),
            ('L', 'Liquid'),
            ('S', 'Sealer'),
            ('M', 'Assign'),
            ] )
    
    lot_shade = fields.Char(string="Lot Shade")