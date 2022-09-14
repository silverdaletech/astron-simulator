from odoo import models, fields, api, _


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_odoo_audit_data = fields.Boolean(
        string='Install odoo audit data module')

