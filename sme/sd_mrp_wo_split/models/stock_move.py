# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import timedelta

class StockMove(models.Model):
    _inherit = 'stock.move'

    original_unit_factor = fields.Float()
    qty_percentage = fields.Float(default=1)

    def _compute_qty_percentage(self):
        """
        Calculate qty percentage in move line.
        qty_percentage will save ration after split the workorder qty
        Return:
            float: move.product_uom_qty / ((production.product_qty - production.qty_produced)) or 1
        """
        for move in self:
            mo = move.raw_material_production_id or move.production_id
            if mo:
                move.qty_percentage = move.product_uom_qty / ((mo.product_qty - mo.qty_produced) or 1)
            else:
                move.qty_percentage = 1.0

    #Override the base module to prevent recompute unit_factor
    @api.depends('product_uom_qty', 'raw_material_production_id',
                 'raw_material_production_id.product_qty',
                 'raw_material_production_id.qty_produced', 'production_id',
                 'production_id.product_qty', 'production_id.qty_produced')
    def _compute_unit_factor(self):
        #Will override origianl unit factor to mrp unit factor
        #Unit_factor use to calculate consumed or done qty in production components line
        #After split unit_factor will change so here we are preventing it change with original factor
        #   because we don't want to lose ration between production and component qty
        for move in self:
            mo = move.raw_material_production_id or move.production_id
            if move.original_unit_factor > 0:
                move.unit_factor = move.original_unit_factor
            elif mo:
                move.unit_factor = move.product_uom_qty / ((mo.product_qty - mo.qty_produced) or 1)
            else:
                move.unit_factor = 1.0

    #Overrider mrp base function to change unit_factor field with percentage fields
    @api.depends('raw_material_production_id.qty_producing', 'product_uom_qty', 'product_uom')
    def _compute_should_consume_qty(self):
        for move in self:
            mo = move.raw_material_production_id
            if not mo or not move.product_uom or move.unit_factor == 0:
                move.should_consume_qty = 0
                continue
            #new calculation based on split qty
            
            move.should_consume_qty = float_round((mo.qty_producing * move.unit_factor) * (move.qty_percentage /  move.unit_factor), precision_rounding=move.product_uom.rounding)

            # odoo calculation based on unit factor 
            # move.should_consume_qty = float_round((mo.qty_producing - mo.qty_produced) * move.unit_factor, precision_rounding=move.product_uom.rounding)
