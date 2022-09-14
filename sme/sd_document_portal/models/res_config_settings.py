# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shared_link_default_deadline = fields.Date(string='Default Shared Link Deadline',
                                               related='company_id.shared_link_default_deadline', readonly=False)
    documents_portal_settings = fields.Boolean(related='company_id.documents_portal_settings', readonly=False,
                                                string="Product")
    portal_folder = fields.Many2one('documents.folder', related='company_id.portal_folder', readonly=False,
                                     string="Portal default workspace")
