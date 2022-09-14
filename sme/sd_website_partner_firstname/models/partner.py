# -*- coding: utf-8 -*-

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Make first and last name editable on website
    def init(self):
        self.env['ir.model.fields'].sudo().formbuilder_whitelist(self._name, ('firstname', 'lastname'))