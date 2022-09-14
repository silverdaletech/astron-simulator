# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_mo_description = fields.Boolean(
        string='MO Description', config_parameter='sd_sale_mrp.is_mo_description',
        required=False)