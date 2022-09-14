# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUser(models.Model):
    """inherit to add portal access right fields"""

    _inherit = 'res.partner'

    enable_sale_portal_access = fields.Boolean(string="Can see Sales Orders and Quotation on Portal", default=True)
    access_all_records = fields.Boolean(string="Can see all company's Sales records", default=True  )
    access_follower_sale_records = fields.Boolean(string="Can see  Sale records where he is a Follower",
                                                       default=True)

    @api.onchange('enable_sale_portal_access')
    def check_record_access(self):
        """uncheck the access on all company record in uncheck the enable sale portal access"""
        if not self.enable_sale_portal_access and self.access_all_records:
            self.access_all_records = False
            self.access_follower_sale_records = False






