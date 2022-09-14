# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUser(models.Model):
    """inherit to add portal access right fields"""

    _inherit = 'res.partner'

    enable_helpdesk_portal_access = fields.Boolean(string="Can see Helpdesk on Portal", default=True)
    access_all_helpdesk_records = fields.Boolean(string="Can see all company's Helpdesk records", default=True  )
    access_follower_helpdesk_records = fields.Boolean(string="Can see  Helpdesk records where he is a follower", default=True  )

    @api.onchange('enable_helpdesk_portal_access')
    def check_helpdesk_record_access(self):
        """uncheck the access on all company record in uncheck the enable sale portal access"""
        if not self.enable_helpdesk_portal_access and self.access_all_helpdesk_records:
            self.access_all_helpdesk_records = False
            self.access_follower_helpdesk_records = False






