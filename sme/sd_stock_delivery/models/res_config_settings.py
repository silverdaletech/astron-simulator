from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_stock_delivery_fedex = fields.Boolean(
        string='Fedex on Delivery Order',
        required=False)
    
    module_sd_stock_delivery_ups = fields.Boolean(
        string='UPS on Delivery Order',
        required=False)

    module_sd_stock_delivery_usps = fields.Boolean(
        string='USPS on Delivery Order',
        required=False)
