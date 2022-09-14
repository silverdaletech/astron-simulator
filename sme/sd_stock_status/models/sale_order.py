# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    """
    sale.order model is inherited to add delivery_status on SO form view
    """
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('done', 'Done'),
        ('over', 'Over')
    ], string='Delivery Status', compute='_get_delivery_status', store=True, readonly=True)


    @api.depends('state', 'order_line.delivery_status', 'order_line.product_id',
                 'order_line.qty_delivered', 'picking_ids')
    def _get_delivery_status(self):
        """
        this computed method is called for delivery_status field according to state, line.delivery_status,Line.qty_delivered, stock.picking id and Line.product_id fields
        """
        for order in self:
            order.delivery_status = False
            if order.picking_ids:
                product_types = ['product', 'consu']
                if order.state not in ['draft', 'cancel']:
                    if all(line.delivery_status == 'done' for line in order.order_line if
                           line.product_id.type in product_types):
                        order.delivery_status = 'done'
                    elif any(line.delivery_status == 'pending' for line in order.order_line if
                             line.product_id.type in product_types):
                        order.delivery_status = 'pending'
                    elif any(line.delivery_status == 'partial' for line in order.order_line if
                             line.product_id.type in product_types):
                        order.delivery_status = 'partial'
                    elif any(line.delivery_status == 'over' for line in order.order_line if
                             line.product_id.type in product_types):
                        order.delivery_status = 'over'
                    else:
                        order.delivery_status = False






class SaleOrderLine(models.Model):
    """
    sale.order.line model is inherited to add delivery_status on SO form view
    """
    _inherit = 'sale.order.line'

    delivery_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('done', 'Done'),
        ('over', 'Over')
    ], string='Delivery Status', compute='_compute_delivery_status', readonly=True, default='pending', store=True)


    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'product_id')
    def _compute_delivery_status(self):
        """
        this computed method is called for delivery_status field, and its value sets according to state, product_uom_qty, qty_delivered and type of product selected
        """
        for line in self:
            line.delivery_status = False
            if line.product_id.type in ['product', 'consu']:
                if line.state not in ['draft', 'cancel']:
                    if line.qty_delivered == line.product_uom_qty:
                        line.delivery_status = 'done'
                    elif line.qty_delivered < line.product_uom_qty and line.qty_delivered != 0:
                        line.delivery_status = 'partial'
                    elif line.qty_delivered > line.product_uom_qty:
                        line.delivery_status = 'over'
                    else:
                        line.delivery_status = 'pending'
