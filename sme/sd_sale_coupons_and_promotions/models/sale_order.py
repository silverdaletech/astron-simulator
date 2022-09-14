# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_reward_total(self):
        """
        When computing the reward total for the order, also compute the promotional_discount, coupon_program_ids
        and discounted_total for the lines.
        """
        res = super(SaleOrder, self)._compute_reward_total()

        show_promotion_details = self.env['ir.config_parameter'].sudo().get_param(
            'sd_sale_coupons_and_promotions.show_promotion_details')

        if show_promotion_details == 'True':
            for order in self:
                order.reward_amount = sum([line.price_subtotal for line in order._get_reward_lines()])

                lines = self._get_paid_order_lines()
                applied_programs = order._get_applied_programs_with_rewards_on_current_order()
                reward_dict = {}
                for program in applied_programs:
                    if program.discount_apply_on in ['specific_products', 'on_order']:
                        if program.discount_apply_on == 'specific_products':
                            lines = lines.filtered(
                                lambda x: x.product_id in (program.discount_specific_product_ids))

                        amount_total = sum(self._get_base_order_lines(program).mapped('price_subtotal'))
                        currently_discounted_amount = 0
                        for line in lines:
                            discount_line_amount = min(self._get_reward_values_discount_percentage_per_line(program, line),
                                                       amount_total - currently_discounted_amount)

                            if line.id in reward_dict:
                                reward_dict[line.id]['promotional_discount'] += discount_line_amount
                                reward_dict[line.id]['coupon_program_ids'].append((4, program.id))
                                reward_dict[line.id]['discounted_total'] -= discount_line_amount
                            else:
                                reward_dict[line.id] = {
                                    'coupon_program_ids': [(4, program.id)],
                                    'promotional_discount': discount_line_amount,
                                    'discounted_total': line.price_subtotal - discount_line_amount
                                }

                            if line.tax_id in reward_dict:
                                continue
                            else:
                                reward_dict[line.tax_id] = {
                                    'name': _(
                                        "Discount: %(program)s - On product with following taxes: %(taxes)s",
                                    ),
                                }
                                currently_discounted_amount += discount_line_amount

                for line in lines:
                    if line.id in reward_dict:
                        line.write(reward_dict.get(line.id))
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    coupon_program_ids = fields.Many2many('coupon.program', string='Promotions Applied')
    promotional_discount = fields.Float(string='Promotional Discount')
    discounted_total = fields.Float(string='Discounted Total')

