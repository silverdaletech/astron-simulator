# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUser(models.Model):
    """inherit to add portal access right fields"""

    _inherit = 'res.partner'

    enable_purchase_portal_access = fields.Boolean(string="Can see Purchase Order & Quotation on Portal", default=True)
    enable_follower_purchase_portal_access = fields.Boolean(string="Can see Purchase records on Portal where he is a follower", default=True)
    access_all_purchase_records = fields.Boolean(string="Can see all company's Purchase records", default=True  )

    @api.onchange('enable_purchase_portal_access')
    def check_purchase_record_access(self):
        """When uncheck the purchase button then it will auto uncheck the all records button"""
        if not self.enable_purchase_portal_access and self.access_all_purchase_records:
            self.access_all_purchase_records = False
            self.enable_follower_purchase_portal_access = False






