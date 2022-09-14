# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_promotion_details = fields.Boolean(
        string='Coupons & Promotions Details in Order Lines', config_parameter='sd_sale_coupon.show_promotion_details')