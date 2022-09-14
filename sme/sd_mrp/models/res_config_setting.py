# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_mrp_split_order = fields.Boolean(
        string='MRP Split Order',
        required=False)

