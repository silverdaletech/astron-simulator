# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ManufacturingSplitOrder(models.Model):
    _inherit = 'mrp.production'

    split_track_ids = fields.One2many('mrp.track.split', 'production_id', string="Split Tracks")

    def write(self, vals):
        if self._context.get('prevent_updating_fields'):
            for field in self._context.get('prevent_updating_fields'):
                if field in vals:
                    del vals[field]
        self = self.with_context(mrp_production_id=self.ids)
        if vals:
            return super(ManufacturingSplitOrder, self).write(vals)
        else:
            return True

    def link_finished(self):
        moves_finished_values = self._get_moves_finished_values()
        self.write({'move_finished_ids': [(0, 0, moves_finished_values[0])]})

    def split_mrp_order(self):
        for rec in self:
            return {
                'name': _('Split Order'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'split.order.wizard',
                'res_id': False,
                'context': {'current_id': rec.id},
                'target': 'new',
            }

    def split_mrp_production(self):
        mo_id_to_split = self.env.context.get('mo_id_to_split', False)
        mo_id_to_split._split_mrp_production(values=self.env.context.get('values', False))
        if self.env.company.split_child_mo:
            child_mo = mo_id_to_split.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids
            values = self.env.context.get('values', False)
            new_vals = []
            while(child_mo):
                for ch_mo in child_mo:
                    for rec in values:
                        vals = {
                            'date': rec['date'],
                            'quantity': ch_mo.product_qty * rec['ratio'],
                            'split_into': rec['split_into'],
                            'is_original': rec['is_original'],
                            'total_quantity': ch_mo.product_qty,
                            'ratio': rec['ratio'],
                        }
                        new_vals.append(vals)
                    ch_mo._split_mrp_production(values=new_vals)
                    new_vals = []
                child_mo = child_mo.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids


    def _generate_backorder_productions(self, close_mo=True):
        return super(ManufacturingSplitOrder, self.with_context(prevent_updating_fields=['backorder_sequence', 'name']))._generate_backorder_productions(close_mo=close_mo)

    def _get_split_backorder_mo_vals(self, split_vals):
        self.ensure_one()
        next_seq = max(self.procurement_group_id.mrp_production_ids.mapped("backorder_sequence"))
        return {
            'name': self._get_name_backorder(self.name, next_seq + 1),
            'backorder_sequence': next_seq + 1,
            'procurement_group_id': self.procurement_group_id.id,
            'move_raw_ids': None,
            'move_finished_ids': None,
            'product_qty': split_vals.get('quantity', False),
            'lot_producing_id': False,
            'origin': self.origin,
            'date_planned_start': split_vals.get('date', False)
        }

    def _split_mrp_production(self, values):
        for production in self:
            # if production.backorder_sequence == 0:  # Activate backorder naming
            #     production.backorder_sequence = 1
            # production.name = self._get_name_backorder(production.name, production.backorder_sequence)
            backorders_list = []
            for index, split in enumerate(values):
                if index != 0:
                    backorder_mo = production.copy(
                        default=production._get_split_backorder_mo_vals(split_vals=split))

                    new_moves_vals = []
                    split_count = split.get('quantity', False)
                    split_into = split.get('split_into', False)

                    for move in production.move_raw_ids | production.move_finished_ids:
                        if not move.additional:
                            move.unit_factor = move.product_uom_qty / (
                                    (production.product_qty - production.qty_produced) or 1)
                            new_qty = self.product_uom_id._compute_quantity(
                                ((split_count) - production.qty_produced) * move.unit_factor,
                                production.product_uom_id,
                                rounding_method='HALF-UP')
                            qty_to_split = new_qty
                            move_vals = move._split(qty_to_split)
                            if not move_vals:
                                continue
                            if move.raw_material_production_id:
                                move_vals[0]['raw_material_production_id'] = backorder_mo.id
                            else:
                                move_vals[0]['production_id'] = backorder_mo.id
                            new_moves_vals.append(move_vals[0])
                    self.env['stock.move'].create(new_moves_vals)

                    t_split_count = split_count * (split_into - (index-1))
                    diff = 0
                    if t_split_count != production.product_qty:
                        diff = production.product_qty - t_split_count
                    if diff:
                        production.product_qty = ((split_count * (split_into - (index-1))) + diff ) - split_count
                    else:
                        production.product_qty = (split_count*(split_into-(index-1)))-split_count

                    # write date of backorder so that it propagates to its moves also
                    if split.get('date', False):
                        backorder_mo.date_planned_start = split.get('date', False)

                    backorders_list.append(backorder_mo)

                if index == 0 and split.get('is_original', False):
                    production.date_planned_start = split.get('date', False)

            production.do_unreserve()
            production.action_assign()
            production.move_raw_ids._recompute_state()

            for backorder in backorders_list:
                backorder.filtered(lambda mo: mo.move_raw_ids).action_confirm()
                backorder.filtered(lambda mo: mo.move_raw_ids).action_assign()
                backorder.move_raw_ids.move_line_ids.filtered(
                    lambda ml: ml.product_id.tracking == 'serial' and ml.product_qty == 0).unlink()
                backorder.move_raw_ids._recompute_state()

            # Track split orders
            backorders_list_ext = backorders_list
            backorders_list_ext.insert(0, production)
            split_lines = []
            for backorder in backorders_list_ext:
                split_lines.append((0, 0, {
                    'split_mo': backorder.id,
                    'split_mo_qty': backorder.product_qty,
                }))
            track_values = [(0, 0, {
                'split_order': production.id,
                'split_into': values[0].get('split_into', False),
                'new_mo': int(values[0].get('split_into', False)) - 1,
                'pre_split_qty': values[0].get('total_quantity', 0),
                'post_split_qty': production.product_qty,
                'split_track_line_ids': split_lines
            })]

            production.write({'split_track_ids': track_values})
            return backorders_list


class MRPTrackSplit(models.Model):
    _name = 'mrp.track.split'
    _description = "Track MRP Split orders"

    production_id = fields.Many2one('mrp.production', string="Production order")
    split_order = fields.Many2one('mrp.production', string="Split order")
    split_into = fields.Integer(string="Split Into")
    new_mo = fields.Integer(string="New Orders")
    pre_split_qty = fields.Float(string="Original Qty")
    post_split_qty = fields.Float(string="Qty After Split")
    split_by = fields.Many2one('res.users', 'Split By', default=lambda self: self.env.user)
    split_time = fields.Datetime(string="Time of Split", default=fields.Datetime.now,)
    split_track_line_ids = fields.One2many('mrp.track.split.lines', 'split_track_id', string="Split Tracks")


class MRPTrackSplitLines(models.Model):
    _name = 'mrp.track.split.lines'
    _description = "Track MRP Split order Lines"

    split_track_id = fields.Many2one('mrp.track.split', string="Tracking ID")
    split_mo = fields.Many2one('mrp.production', string="Split MO")
    split_mo_qty = fields.Float(string="Split Qty")


class StockMoves(models.Model):
    _inherit = 'stock.move'

    def _set_date_deadline(self, new_deadline):
        production_id = self.env['mrp.production'].search([('id', 'in', self.env.context.get('mrp_production_id', False))])
        moves_to_be_added_to_already_propagate_ids = []
        if production_id and production_id.split_track_ids:
            if production_id.split_track_ids.split_track_line_ids:
                for line in production_id.split_track_ids.split_track_line_ids.filtered(lambda m: m.split_mo != production_id):
                    if line.split_mo and line.split_mo.move_raw_ids:
                        for move in line.split_mo.move_raw_ids:
                            moves_to_be_added_to_already_propagate_ids.append(move.id)
            if moves_to_be_added_to_already_propagate_ids:
                already_propagate_ids = self.env.context.get('date_deadline_propagate_ids', set()) | set(moves_to_be_added_to_already_propagate_ids)
                self = self.with_context(date_deadline_propagate_ids=already_propagate_ids)

        return super(StockMoves, self)._set_date_deadline(new_deadline)
