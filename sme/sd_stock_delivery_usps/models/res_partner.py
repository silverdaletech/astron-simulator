from odoo import fields, models, api, _ 


class ResPartner(models.Model):
    _inherit = 'res.partner'

    usps_username = fields.Char(string='USPS User ID')