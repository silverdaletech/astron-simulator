from odoo import models, fields, api, _

class ResCountry(models.Model):
    _inherit = 'res.company'

    split_child_mo = fields.Boolean()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    split_child_mo = fields.Boolean(
        string='Split Child MO Also', related="company_id.split_child_mo", readonly=False)