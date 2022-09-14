# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_account_check_printing = fields.Boolean(
        string='Silverdale Check Printing Base',
        required=False)

    module_sd_l10n_ca_check_printing = fields.Boolean(
        string='Silverdale CA Checks Layout',
        required=False)

    module_sd_l10n_us_check_printing = fields.Boolean(
        string='Silverdale US Checks Layout',
        required=False)

    module_sd_equipment_to_asset = fields.Boolean(
        string='Silverdale Equipment to Asset',
        required=False)

