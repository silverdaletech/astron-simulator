# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_purchase_equipment = fields.Boolean("Purchase Equipment",
        related="company_id.is_purchase_equipment",
        readonly=False)

    purchase_equipment = fields.Selection(
        related="company_id.purchase_equipment",
        string="Equipment is created upon",
        readonly=False, required=False,)

    @api.onchange('is_purchase_equipment')
    def _onchange_is_purchase_equipment(self):
        if not self.is_purchase_equipment:
            self.purchase_equipment = False 
        else:
            self.purchase_equipment = self.company_id.purchase_equipment
