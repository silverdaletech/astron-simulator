# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import timedelta

_logger = logging.getLogger(__name__)


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    # next_split_operation_id = fields.Char(default='sd_mrp_wo_split.mrp_routing_workcenter_9999_0')

    # check logs from js
    # @api.model
    # def check_logs(self, tes):
    #     _logger.info("############################################# {}".format(tes))

    # Silverdale remove it
    # #Override base function
    # def _generate_backorder_productions(self, close_mo=True):
    #     backorders = self.env['mrp.production']
    #     for production in self:
    #         if production.backorder_sequence == 0:  # Activate backorder naming
    #             production.backorder_sequence = 1
    #         production.name = self._get_name_backorder(production.name, production.backorder_sequence)
    #         backorder_mo = production.copy(default=production._get_backorder_mo_vals())
    #         if close_mo:
    #             production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write({
    #                 'raw_material_production_id': backorder_mo.id,
    #             })
    #             production.move_finished_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write({
    #                 'production_id': backorder_mo.id,
    #             })
    #         else:
    #             new_moves_vals = []
    #             for move in production.move_raw_ids | production.move_finished_ids:
    #                 if not move.additional:
    #                     # Change unit_factor with qty_percentage
    #                     qty_to_split = move.product_uom_qty - move.qty_percentage * production.qty_producing
    #                     # Odoo code
    #                     # qty_to_split = move.product_uom_qty - move.unit_factor * production.qty_producing
    #                     qty_to_split = move.product_uom._compute_quantity(qty_to_split, move.product_id.uom_id, rounding_method='HALF-UP')
    #                     move_vals = move._split(qty_to_split)
    #                     if not move_vals:
    #                         continue
    #                     if move.raw_material_production_id:
    #                         move_vals[0]['raw_material_production_id'] = backorder_mo.id
    #                     else:
    #                         move_vals[0]['production_id'] = backorder_mo.id
    #                     new_moves_vals.append(move_vals[0])
    #             self.env['stock.move'].create(new_moves_vals)
    #         backorders |= backorder_mo

    #         # We need to adapt `duration_expected` on both the original workorders and their
    #         # backordered workorders. To do that, we use the original `duration_expected` and the
    #         # ratio of the quantity really produced and the quantity to produce.
    #         ratio = production.qty_producing / production.product_qty
    #         for workorder in production.workorder_ids:
    #             workorder.duration_expected = workorder.duration_expected * ratio
    #         for workorder in backorder_mo.workorder_ids:
    #             workorder.duration_expected = workorder.duration_expected * (1 - ratio)

    #     # As we have split the moves before validating them, we need to 'remove' the excess reservation
    #     if not close_mo:
    #         self.move_raw_ids.filtered(lambda m: not m.additional)._do_unreserve()
    #         self.move_raw_ids.filtered(lambda m: not m.additional)._action_assign()
    #     backorders.action_confirm()

    #     # Remove the serial move line without reserved quantity. Post inventory will assigned all the non done moves
    #     # So those move lines are duplicated.
    #     backorders.move_raw_ids.move_line_ids.filtered(lambda ml: ml.product_id.tracking == 'serial' and ml.product_qty == 0).unlink()

    #     wo_to_cancel = self.env['mrp.workorder']
    #     wo_to_update = self.env['mrp.workorder']
    #     for old_wo, wo in zip(self.workorder_ids, backorders.workorder_ids):
    #         if old_wo.qty_remaining == 0:
    #             wo_to_cancel += wo
    #             continue
    #         if not wo_to_update or wo_to_update[-1].production_id != wo.production_id:
    #             wo_to_update += wo
    #         wo.qty_produced = max(old_wo.qty_produced - old_wo.qty_producing, 0)
    #         if wo.product_tracking == 'serial':
    #             wo.qty_producing = 1
    #         else:
    #             wo.qty_producing = wo.qty_remaining
    #         # Update assgin_qty based on percentage
    #         old_wo.assign_qty = old_wo.qty_percentage * old_wo.qty_producing
    #         wo.assign_qty = wo.qty_percentage * wo.qty_producing
    #     wo_to_cancel.action_cancel()
    #     for wo in wo_to_update:
    #         wo.state = 'ready' if wo.next_work_order_id.production_availability == 'assigned' else 'waiting'

    #     return backorders
