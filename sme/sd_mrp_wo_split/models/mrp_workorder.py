# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools import float_compare, float_round, format_datetime
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from odoo.exceptions import UserError
import json


class MRPWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    # split_wo_line = fields.One2many('workorder.split.line', 'workorder_id')
    # assign_qty = fields.Float(string="Work Order Quantity")
    # qty_percentage = fields.Float(default=1)
    # original_workorder_id = fields.Many2one('mrp.workorder')
    # split_from = fields.Many2one('mrp.workorder')
    # split_to = fields.One2many('mrp.workorder', 'split_from')

    # Silverdale remove it
    # def action_move_workcenter(self):
    #     """
    #     Create new workorder based on qty
    #     Create new stock move and link with new created workorder
    #     Change existing qty based on split qty
    #     """
    #     if sum(self.split_wo_line.filtered(lambda x: not x.is_done).mapped('qty')) > self.assign_qty:
    #         raise ValidationError(
    #             _('{} Assigned quantity cannot be greater then work order quantity.'.format(self.name)))

    #     for line in self.split_wo_line.filtered(lambda x: not x.is_done and x.qty > 0):
    #         #Operation id should be unique for production move line
    #         # same operation will merge move line
    #         opertaion_id = False
    #         opertaion = self.production_id.next_split_operation_id
    #         if opertaion:
    #             try:
    #                 opertaion_id = self.env.ref(opertaion).id
    #             except:
    #                 raise ValidationError(_('You cannot split more workcenter'))
    #         line.operation_id = opertaion_id
    #         self.assign_qty -= line.qty
    #         # workOrder_id = self.copy({'move_raw_ids' :False})
    #         workorder_id = self.env['mrp.workorder']
    #         vals = {
    #             'product_id': self.product_id.id,
    #             'workcenter_id': line.workcenter_id.id,
    #             'name': line.name,
    #             'component_id': self.component_id.id,
    #             'production_bom_id': self.production_bom_id.id,
    #             'operation_id': line.operation_id.id,
    #             'product_uom_id': self.production_id.product_uom_id.id,
    #             'production_id': self.production_id.id,
    #             'qty_production': self.qty_production,
    #             'qty_remaining': self.qty_remaining,
    #             'assign_qty':  line.qty,
    #             'quality_point_ids':  self.quality_point_ids,
    #             'qty_percentage': line.qty / self.qty_production,
    #             'split_from': self.id,
    #             'original_workorder_id': self.original_workorder_id.id,
    #         }
    #         self.qty_percentage = self.assign_qty / self.qty_production
    #         workorder_id = workorder_id.create(vals)
    #         # move_id = self.move_id.copy({'workorder_id': workOrder_id.id})
    #         workorder_id.duration_expected = workorder_id._get_duration_expected()
    #         # workOrder_id.move_id = (4, move_id.id)
    #         for rec in self.move_raw_ids:
    #             opertaion_id = False
    #             if rec.operation_id:
    #                 opertaion_id = line.operation_id.id
    #             rec.original_unit_factor = rec.unit_factor
    #             new_qty = line.qty * rec.unit_factor
    #             rec.product_uom_qty -= new_qty
    #             vals = {
    #                 'bom_line_id': rec.bom_line_id.id,
    #                 'origin': rec.origin,
    #                 'location_id': rec.location_id.id,
    #                 'location_dest_id': rec.location_dest_id.id,
    #                 'product_id': rec.product_id.id,
    #                 'workorder_id': workorder_id.id,
    #                 'company_id': rec.company_id.id,
    #                 'group_id': rec.group_id.id,
    #                 'original_unit_factor': rec.original_unit_factor,
    #                 'product_uom_qty': new_qty,
    #                 'name':'new',
    #                 'procure_method': rec.procure_method,
    #                 'picking_type_id': rec.picking_type_id.id,
    #                 'product_uom': rec.product_uom.id,
    #                 'operation_id': opertaion_id,
    #                 'raw_material_production_id': rec.raw_material_production_id.id,
    #             }
    #             mv = self.env['stock.move'].create(vals)
    #             mv._compute_qty_percentage()
    #             self.production_id.action_confirm()
    #             workorder_id.move_raw_ids = [(4, mv.id)]
    #         next_operation = int(opertaion.split('_')[-1])
    #         opertaion = opertaion[:-1] + str(next_operation +1)
    #         self.production_id.next_split_operation_id = opertaion
    #         line.is_done = True

    #     self.move_raw_ids._compute_qty_percentage()

    # silverdale remove it
    # def action_split(self):
    #     """
    #         Return xml action to open split form
    #     """
    #     view = self.env.ref('sd_mrp_wo_split.mrp_workorder_form_split_form')
    #     if not self.split_wo_line:
    #         if self.assign_qty == 0:
    #             self.assign_qty = self.qty_production
    #         self.original_workorder_id = self.id
    #         #Create split line when click on split button.
    #         for index, workdorder in enumerate(self.workcenter_id.alternative_workcenter_ids):
    #             self.write({
    #                 'split_wo_line':[(0, 0, {
    #                     'name': '{}-{}'.format(self.name, index + 1),
    #                     'workcenter_id': workdorder.id
    #                 })]
    #             })
    #     return {
    #         'name': _('Move Workorder'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mrp.workorder',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': self.id,
    #         'context': {}
    #     }

    def action_view_consumption(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.workcenter.productivity',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('sd_mrp_wo_split.mrp_workcenter_productivity_view_tree').id, 'tree'),
                (False, 'form')],
            'name': _('Productivity'),
            'target': 'new',
            'context':{
                'create': False,
                'delete': False,
                'no_breadcrumbs': True,
                'readonly': True
            },
            'clear_breadcrumb': True,
            'domain': [('workorder_id', '=', self.id)],
            'res_id': self.id,
        }

    # Sivlerdale Remove it
    def button_pending(self):
        result = self.check_worklog('button_pending')
        if not result:
            res = super(MRPWorkorder, self).button_pending()
            if self.workcenter_id.user_id:
                if self.workcenter_id.user_id.id == self.env.user.id:
                    self.button_start()
            # res.button_start()
            return res
        return result

    def button_finish(self):
        
        if len(self) > 1:
            result = self[0].check_worklog('button_finish')
        else:
            result = self.check_worklog('button_finish')
        
        if not result:
            return super(MRPWorkorder, self).button_finish()
        return result

    def do_finish(self):
        result = self.check_worklog('do_finish')
        if not result:
            return super(MRPWorkorder, self).do_finish()
        return result

    def record_production(self):
        result = self.check_worklog('record_production')
        # no_start_next
        if not result:
            return super(MRPWorkorder, self.with_context(no_start_next=True)).record_production()
        return result

    def action_next(self):
        result = self.check_worklog('action_next')
        if not result:
            return super(MRPWorkorder, self).action_next()
        return result

    def check_worklog(self, call_from=False):
        timeline_obj = self.env['mrp.workcenter.productivity']
        domain = [
            ('workorder_id', 'in', self.ids),
            ('date_end', '=', False),
            ('is_added_qty', '=', False),
            ('user_id', '=', self.env.user.id)
        ]

        timeline = timeline_obj.search(domain)
        if timeline:
            domain = [
                ('workorder_id', 'in', self.ids)
            ]
            total_qty = sum(timeline_obj.search(domain).mapped('produced_qty'))
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'wo.produced.qty.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(self.env.ref('sd_mrp_wo_split.wo_produced_qty_wizard_view').id, 'form')],
                'name': _('Productivity'),
                'target': 'new',
                'context':{
                    # 'default_workorder_id': self.filtered(lambda w: w.id == self.env.context.get('active_id')).id,
                    'default_workorder_id': self.id,
                    'default_doall': True,
                    'default_total_worklog_qty': total_qty,
                    'default_date_start': timeline[0].date_start,
                    # 'default_date_end': datetime.now(),
                    'call_from': call_from,
                }
            }
        return False

    def _prepare_timeline_vals(self, duration, date_start, date_end=False):
        res = super(MRPWorkorder, self)._prepare_timeline_vals(duration, date_start, date_end)
        if self._context.get('default_date_start', False):
            res['date_start'] = self._context.get('default_date_start', False)
            # if self.workcenter_id.user_id :
            #     res['user_id'] = self.workcenter_id.user_id.id
        return res

    # Sivlerdale Remove it
    # def open_tablet_view(self):
    #     """
    #     Update lot_id in Checks to populate lot_it field in tablet view.
    #     """
    #     res = super(MRPWorkorder, self).open_tablet_view()

    #     if self.check_ids and self.production_id:
    #         if not self.current_quality_check_id or not self.current_quality_check_id.lot_id:
    #             for check in self.check_ids:
    #                 if self.check_ids.mapped('move_id').filtered(
    #                         lambda m: m.product_id == check.component_id).move_line_ids and \
    #                         self.check_ids.mapped('move_id').filtered(
    #                                 lambda m: m.product_id == check.component_id).move_line_ids[0].lot_id:
    #                     check.lot_id = self.check_ids.mapped('move_id').filtered(
    #                         lambda m: m.product_id == check.component_id).move_line_ids[0].lot_id.id
    #     return res