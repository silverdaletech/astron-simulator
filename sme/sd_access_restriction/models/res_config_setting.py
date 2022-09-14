from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_ip_restrict = fields.Boolean(
        string='IP base Restriction', config_parameter='sd_access_restriction.is_ip_restrict', required=False)
    is_mac_restrict = fields.Boolean(
        string='Mac base Restriction', config_parameter='sd_access_restriction.is_mac_restrict', required=False)
