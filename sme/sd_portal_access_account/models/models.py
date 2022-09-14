# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUser(models.Model):
    """inherit to add portal access right fields"""

    _inherit = 'res.partner'

    enable_invoice_portal_access = fields.Boolean(string="Can see Invoices on Portal", default=True)
    access_all_invoice_records = fields.Boolean(string="Can see all company's Invoices records", default=True  )
    enable_follower_invoice_portal_access = fields.Boolean(string="Can see all  Invoices records where he is a follower", default=True  )

    @api.onchange('enable_invoice_portal_access')
    def check_accounting_record_access(self):
        """uncheck the access on all company record in uncheck the enable sale portal access"""
        if not self.enable_invoice_portal_access and self.access_all_invoice_records:
            self.access_all_invoice_records = False
            self.enable_follower_invoice_portal_access = False






