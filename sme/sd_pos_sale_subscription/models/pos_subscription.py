# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class POSSubscription(models.Model):
    _inherit = "sale.subscription"

    created_from_pos = fields.Boolean(compute='_compute_created_from_pos')

    def _compute_created_from_pos(self):
        """
        Check if subscription is created from POS
        """
        for sub in self:
            created_from_pos = False
            pos_order_id = self.env['pos.order'].search([('lines.subscription_id', '=', sub.id)])
            if pos_order_id:
                created_from_pos = True
            sub.created_from_pos = created_from_pos

    def action_open_pos_sales(self):
        """
        If there are pos orders which has subscription line with self.id, goto pos order.
        """
        self.ensure_one()
        pos_order_id = self.env['pos.order'].search([('lines.subscription_id', 'in', self.ids)])
        return {
            "type": "ir.actions.act_window",
            "res_model": "pos.order",
            'view_mode': 'form',
            "res_id": pos_order_id.id,
            "context": {"create": False},
            "name": _("POS Orders"),
        }