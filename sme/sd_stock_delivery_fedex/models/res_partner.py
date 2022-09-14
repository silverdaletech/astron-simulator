# -*- coding: utf-8 -*-

from odoo import api, models, fields, _, tools
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    #Fedex
    fedex_account_number = fields.Char(string="FedEx Account Number", groups="base.group_system")
