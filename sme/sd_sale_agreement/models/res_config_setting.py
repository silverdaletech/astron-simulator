from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_disable_sa_warning = fields.Boolean(
        string='Disable SA Warning ?', config_parameter='sd_sale_agreement.is_disable_sa_warning',
        required=False)
