# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command


class PosSession(models.Model):
    _inherit = 'pos.session'

    def get_closing_control_data(self):
        """
        Inherit this method to add tips amount to the order_details that will be returned to the closing stats screen js.
        """
        res = super(PosSession, self).get_closing_control_data()
        tip_product_id = self.config_id.tip_product_id
        show_tips_in_closing_stats = self.config_id.show_tips_in_closing_stats

        if tip_product_id and show_tips_in_closing_stats:
            orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
            tip_amount = 0
            for order in orders:
                tip_amount += sum(order.lines.filtered(lambda line: line.product_id == tip_product_id).mapped('price_subtotal_incl'))
            res['orders_details'].update({'tips': tip_amount})

        return res
