# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    """
    sale.order model is inherited to add manufacturing_status and invoice_status on SO form view
    """
    _inherit = 'sale.order'

    manufacturing_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('done', 'Done'),
        ('over', 'Over')
    ], string='Manufacturing Status', compute='_get_manufacturing_status', readonly=True, store=True)
    invoice_status_related = fields.Selection(string="Invoice Status", related='invoice_status')
    mo = fields.Boolean(compute='_compute_manufactured_qty')

    def _compute_manufactured_qty(self):
        mo = False
        for line in self.order_line:
            if line.product_id.type in ['product', 'consu']:
                line._compute_manufactured_qty()
                if line.mo:
                    mo = True
        self.mo = mo

    @api.depends('state', 'order_line.manufacturing_status', 'order_line.product_id', 'order_line.mo_qty',
                 'procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids')
    def _get_manufacturing_status(self):
        """
        this computed method is called for manufacturing_status field according to state, line.MO, and Line.qty fields
        """
        for order in self:
            order.manufacturing_status = False
            manufacturing_orders = self.env['mrp.production'].search([('origin', '=', order.name)])
            if manufacturing_orders:
                product_types = ['product', 'consu']
                if order.state not in ['draft', 'cancel']:
                    if all(line.manufacturing_status == 'done' for line in order.order_line if
                           line.product_id.detailed_type in product_types and line.id in manufacturing_orders.mapped(
                               'sale_line_id.id')):
                        order.manufacturing_status = 'done'
                    elif all(line.manufacturing_status == 'pending' for line in order.order_line if
                             line.product_id.detailed_type in product_types and line.id in manufacturing_orders.mapped(
                                 'sale_line_id.id')):
                        order.manufacturing_status = 'pending'
                    elif (not any(line.manufacturing_status == 'pending' for line in order.order_line if
                                 line.product_id.detailed_type in product_types and line.id in manufacturing_orders.mapped(
                                     'sale_line_id.id')) and not any(
                        line.manufacturing_status == 'partial' for line in order.order_line if
                        line.product_id.detailed_type in product_types and line.id in manufacturing_orders.mapped(
                            'sale_line_id.id'))) and any(line.manufacturing_status == 'over' for line in order.order_line if
                                 line.product_id.detailed_type in product_types and line.id in manufacturing_orders.mapped('sale_line_id.id')):
                        order.manufacturing_status = 'over'
                    else:
                        order.manufacturing_status = 'partial'


class SaleOrderLine(models.Model):
    """
    sale.order.line model is inherited to add mo, mo_qty, inv_condition and manufacturing_status on SO form view
    """
    _inherit = 'sale.order.line'

    inv_condition = fields.Boolean(default=True, compute='_compute_manufactured_qty')
    mo = fields.Boolean(compute='_compute_manufactured_qty')

    manufacturing_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('done', 'Done'),
        ('over', 'Over')
    ], string='Manufacturing Status', compute='_compute_manufacturing_status', readonly=True, store=True)
    mo_qty = fields.Float(string='Manufactured Qty', compute='_compute_manufactured_qty', store=True)

    @api.depends(
        'order_id.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.qty_producing',
        'order_id.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.state')
    def _compute_manufactured_qty(self):
        """
        this computed method sets values for fields mo, mo_qty and inv_condition , According to state of mrp_production_ids and quantity of mrp_production_ids
        """
        for line in self:
            line.mo_qty = False
            line.mo = False
            line.inv_condition = True
            if line.product_id.detailed_type in ['product', 'consu']:
                mos = self.env['mrp.production'].search([('origin', '=', line.order_id.name)])
                mos_done = mos.filtered(lambda m: m.state == 'done')
                mos_not_done = mos.filtered(lambda m: m.state != 'done')

                if not mos:
                    line.mo = True
                    line.mo_qty = False
                for mo in mos_done:
                    if line.product_id == mo.product_id and line.id == mo.sale_line_id.id:
                        line.inv_condition = False
                        line.mo_qty = line.mo_qty + mo.qty_producing
                if not mos_done and mos_not_done:
                    for mo in mos_not_done:
                        if line.product_id == mo.product_id and line.id == mo.sale_line_id.id:
                            line.inv_condition = False
                            line.mo_qty = 0.0

    @api.depends('state', 'product_uom_qty', 'product_id', 'mo_qty')
    def _compute_manufacturing_status(self):
        """
        this computed method sets tha value of field manufacturing_status according to state, product_uom_qty and type of product in line items and mo_qty field value
        """
        for line in self:
            line.manufacturing_status = False
            if line.product_id.detailed_type in ['product', 'consu']:
                if line.state not in ['draft', 'cancel']:
                    mos = self.env['mrp.production'].search([('origin', '=', line.order_id.name)])
                    if mos:
                        if line.mo_qty == line.product_uom_qty and line.product_uom_qty != 0 and line.id in mos.mapped(
                                'sale_line_id.id'):
                            line.manufacturing_status = 'done'
                        elif line.mo_qty < line.product_uom_qty and line.mo_qty != 0 and line.id in mos.mapped(
                                'sale_line_id.id'):
                            line.manufacturing_status = 'partial'
                        elif line.mo_qty > line.product_uom_qty and line.id in mos.mapped('sale_line_id.id'):
                            line.manufacturing_status = 'over'
                        elif line.mo_qty == 0 and line.product_uom_qty != 0 and line.id in mos.mapped(
                                'sale_line_id.id'):
                            line.manufacturing_status = 'pending'
                        else:
                            line.manufacturing_status = False
