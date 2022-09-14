# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_document_portal = fields.Boolean(
        string='Documents on Portal',
        required=False)
