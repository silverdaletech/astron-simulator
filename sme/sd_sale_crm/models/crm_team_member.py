# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class Team(models.Model):
    _inherit = 'crm.team.member'

    show_allow_offer = fields.Selection(related="company_id.crm_product_price_rule")
    
    allow_offer = fields.Boolean(string="Allow offer",
                    help="Allow offering Custom Prices?")
    allow_percentage = fields.Float()
    

    #--------------------------------------------------
    # Constraints
    #--------------------------------------------------


    @api.constrains('allow_percentage')
    def _check_allow_percentage(self):
        for record in self:
            if record.allow_percentage:
                if record.allow_percentage < 1:
                    raise ValidationError("Percentage should be greater then 0")
                elif record.allow_percentage > 100:
                    raise ValidationError("Percentage should not greater then to 100")