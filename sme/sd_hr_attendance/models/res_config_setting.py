# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_portal_attendance = fields.Boolean(string="Attendance On Portal?",
                                        related='company_id.is_portal_attendance',
                                        readonly=False)

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_portal_attendance = fields.Boolean(string="Show Attendance Portal")
