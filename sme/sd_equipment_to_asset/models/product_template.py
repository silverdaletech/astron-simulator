# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_equipment = fields.Boolean('Equipment')
    equipment_category = fields.Many2one('maintenance.equipment.category', string="Equipment Category")
    maintenance_team_id = fields.Many2one('maintenance.team', string="Maintenance Team")    
    technician_user_id = fields.Many2one('res.users', string="Technician")

    @api.onchange('detailed_type')
    def _onchange_detailed_type_equip(self):
        if self.detailed_type != 'consu':
            self.is_equipment = False