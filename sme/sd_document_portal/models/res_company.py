# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from email.policy import default
from odoo import api, fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    def _domain_company(self):
        company = self.env.company
        return ['|', ('company_id', '=', False), ('company_id', '=', company.id)]

    documents_portal_settings = fields.Boolean(default=True)
    portal_folder = fields.Many2one('documents.folder', string="Portal Workspace", domain=_domain_company,
                                     default=lambda self: self.env.ref('sd_document_portal.documents_portal_folder',
                                                                       raise_if_not_found=False))
    shared_link_default_deadline = fields.Date()
