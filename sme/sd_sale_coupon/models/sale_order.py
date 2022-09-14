# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

class SaleOrder(models.Model):
    _inherit = "sale.order"

    #odoo base method
    def recompute_coupon_lines(self):
        for order in self:
            # Remove applied coupons from sale order line
            order.order_line.coupon_program_ids = False
            # Set Promotional discount = 0
            order.order_line.write({'promotional_discount': 0})
            order._remove_invalid_reward_lines()
            if order.state != 'cancel':
                order._create_new_no_code_promo_reward_lines()
            order._update_existing_reward_lines()
    
    #odoo base method
    def _remove_invalid_reward_lines(self):
        """ Find programs & coupons that are not applicable anymore.
            It will then unlink the related reward order lines.
            It will also unset the order's fields that are storing
            the applied coupons & programs.
            Note: It will also remove a reward line coming from an archive program.
        """
        self.ensure_one()
        order = self

        applied_programs = order._get_applied_programs()
        applicable_programs = self.env['coupon.program']
        if applied_programs:
            applicable_programs = order._get_applicable_programs() + order._get_valid_applied_coupon_program()
            applicable_programs = applicable_programs._keep_only_most_interesting_auto_applied_global_discount_program()

        # odoo handle by substracting
        # we are handling in by adding because we  just need one progrma
        programs_to_remove = applicable_programs + applied_programs

        # if order have code then removed all program
        if order.code_promo_program_id:
            if order.code_promo_program_id in applicable_programs:
                programs_to_remove = programs_to_remove - order.code_promo_program_id

        reward_product_ids = applied_programs.discount_line_product_id.ids
        # delete reward line coming from an archived coupon (it will never be updated/removed when recomputing the order)
        invalid_lines = order.order_line.filtered(lambda line: line.is_reward_line and line.product_id.id not in reward_product_ids)

        if programs_to_remove:
            product_ids_to_remove = programs_to_remove.discount_line_product_id.ids

            if product_ids_to_remove:
                # Invalid generated coupon for which we are not eligible anymore ('expired' since it is specific to this SO and we may again met the requirements)
                self.generated_coupon_ids.filtered(lambda coupon: coupon.program_id.discount_line_product_id.id in product_ids_to_remove).write({'state': 'expired'})

            # Reset applied coupons for which we are not eligible anymore ('valid' so it can be use on another )
            coupons_to_remove = order.applied_coupon_ids.filtered(lambda coupon: coupon.program_id in programs_to_remove)
            coupons_to_remove.write({'state': 'new'})

            # Unbind promotion and coupon programs which requirements are not met anymore
            order.no_code_promo_program_ids -= programs_to_remove
            order.code_promo_program_id -= programs_to_remove

            if coupons_to_remove:
                order.applied_coupon_ids -= coupons_to_remove

            # Remove their reward lines
            if product_ids_to_remove:
                invalid_lines |= order.order_line.filtered(lambda line: line.product_id.id in product_ids_to_remove)

        invalid_lines.unlink()


    def _get_reward_values_discount(self, program):
        if program.discount_type == 'fixed_amount':
            product_taxes = program.discount_line_product_id.taxes_id.filtered(lambda tax: tax.company_id == self.company_id)
            taxes = self.fiscal_position_id.map_tax(product_taxes)
            return [{
                'name': _("Discount: %s", program.name),
                'product_id': program.discount_line_product_id.id,
                'price_unit': - self._get_reward_values_discount_fixed_amount(program),
                'product_uom_qty': 1.0,
                'product_uom': program.discount_line_product_id.uom_id.id,
                'is_reward_line': True,
                'tax_id': [(4, tax.id, False) for tax in taxes],
            }]
        reward_dict = {}
        lines = self._get_paid_order_lines()
        amount_total = sum([any(line.tax_id.mapped('price_include')) and line.price_total or line.price_subtotal
                            for line in self._get_base_order_lines(program)])

        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line()
            if line:
                discount_line_amount = min(line.price_reduce * (program.discount_percentage / 100), amount_total)
                if discount_line_amount:
                    taxes = self.fiscal_position_id.map_tax(line.tax_id)
                    # store promotional discount
                    line.promotional_discount = - discount_line_amount if discount_line_amount > 0 else 0
                    # Add program id in many2many field
                    line.coupon_program_ids = [(4, program.id)]
                    line.discounted_total = line.price_subtotal - discount_line_amount if discount_line_amount > 0 else 0
                    reward_dict[line.tax_id] = {
                        'name': _("Discount: %s", program.name),
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                        'product_uom_qty': 1.0,
                        'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in taxes],
                    }
        elif program.discount_apply_on in ['specific_products', 'on_order']:
            if program.discount_apply_on == 'specific_products':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['coupon.program'].search([('reward_type', '=', 'product'), ('reward_product_id', 'in', program.discount_specific_product_ids.ids)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.product_id in (program.discount_specific_product_ids | free_product_lines))
            # when processing lines we should not discount more than the order remaining total
            currently_discounted_amount = 0

            applicable_promotion = self._get_applied_programs_with_rewards_on_current_order()
            applicable_promotion = self._get_applicable_no_code_promo_program()
            applicable_promotion = applicable_promotion._keep_only_most_interesting_auto_applied_global_discount_program()
            
            # If user apply code then removed all promotion code
            if self.code_promo_program_id:
                applicable_promotion = self.code_promo_program_id

            for line in lines.filtered(lambda x: not x.coupon_program_ids):
 
                applicable_promotion = applicable_promotion.filtered(lambda x: line.product_id in x.discount_specific_product_ids or x.discount_apply_on == 'on_order')
                applicable_promotion = applicable_promotion.sorted('discount_percentage', reverse = True)
                # if program is not applicable then try next line
                if not applicable_promotion:
                    continue
                # if applicable_promotion is then then apply it
                if len(applicable_promotion) == 1:
                    pass
                else:
                    program = applicable_promotion[0]
                
                #store  applied program
                line.coupon_program_ids = [(4, program.id)]
                discount_line_amount = min(self._get_reward_values_discount_percentage_per_line(program, line), amount_total - currently_discounted_amount)
                if discount_line_amount:
                    # save promotion discount
                    line.promotional_discount = - discount_line_amount if discount_line_amount > 0 else 0
                    line.discounted_total = line.price_subtotal - discount_line_amount if discount_line_amount > 0 else 0
                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]['price_unit'] -= discount_line_amount
                    else:
                        taxes = self.fiscal_position_id.map_tax(line.tax_id)

                        reward_dict[line.tax_id] = {
                            'name': _(
                                "Discount: %(program)s - On product with following taxes: %(taxes)s",
                                program=program.name,
                                taxes=", ".join(taxes.mapped('name')),
                            ),
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                            'product_uom_qty': 1.0,
                            'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_id': [(4, tax.id, False) for tax in taxes],
                        }
                        currently_discounted_amount += discount_line_amount

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()


    def _get_applied_programs_with_rewards_on_current_order(self):
        # Need to add filter on current order. Indeed, it has always been calculating reward line even if on next order (which is useless and do calculation for nothing)
        # This problem could not be noticed since it would only update or delete existing lines related to that program, it would not find the line to update since not in the order
        # But now if we dont find the reward line in the order, we add it (since we can now have multiple line per  program in case of discount on different vat), thus the bug
        # mentionned ahead will be seen now
        if self.applied_coupon_ids.mapped('program_id'):
            return self.applied_coupon_ids.mapped('program_id')
        if self.code_promo_program_id.filtered(lambda p: p.promo_applicability == 'on_current_order'):
            return self.code_promo_program_id.filtered(lambda p: p.promo_applicability == 'on_current_order')
        
        return self.no_code_promo_program_ids.filtered(lambda p: p.promo_applicability == 'on_current_order')

    # odoo base method
    def _create_reward_line(self, program):
        # apply only where line have not coupon program
        lines = self._get_paid_order_lines()
        if lines.filtered(lambda x: not x.coupon_program_ids):
            self.write({'order_line': [(0, False, value) for value in self._get_reward_line_values(program)]})
    
    def _create_new_no_code_promo_reward_lines(self):
        '''Apply new programs that are applicable'''
        self.ensure_one()
        order = self
        programs = order._get_applicable_no_code_promo_program()
        programs = programs._keep_only_most_interesting_auto_applied_global_discount_program()

        #  If user has apply code then removed all previous code
        if self.code_promo_program_id:
            programs = self.code_promo_program_id
        # Add sorted by highed discount
        for program in programs.sorted('discount_percentage', reverse = True):
            # VFE REF in master _get_applicable_no_code_programs already filters programs
            # why do we need to reapply this bunch of checks in _check_promo_code ????
            # We should only apply a little part of the checks in _check_promo_code...
            error_status = program._check_promo_code(order, False)
            if not error_status.get('error'):
                if program.promo_applicability == 'on_next_order':
                    order.state != 'cancel' and order._create_reward_coupon(program)
                elif program.discount_line_product_id.id not in self.order_line.mapped('product_id').ids:
                    # applied program where line have no program id
                    lines = self._get_paid_order_lines()
                    if lines.filtered(lambda x: not x.coupon_program_ids):
                        self.write({'order_line': [(0, False, value) for value in self._get_reward_line_values(program)]})
                    else:
                        continue
                order.no_code_promo_program_ids |= program

    def _update_existing_reward_lines(self):
        '''Update values for already applied rewards'''
        def update_line(order, lines, values):
            '''Update the lines and return them if they should be deleted'''
            lines_to_remove = self.env['sale.order.line']
            # Check commit 6bb42904a03 for next if/else
            # Remove reward line if price or qty equal to 0
            if values['product_uom_qty'] and values['price_unit']:
                lines.write(values)
            else:
                if program.reward_type != 'free_shipping':
                    # Can't remove the lines directly as we might be in a recordset loop
                    lines_to_remove += lines
                else:
                    values.update(price_unit=0.0)
                    lines.write(values)
            return lines_to_remove

        self.ensure_one()
        order = self
        applied_programs = order._get_applied_programs_with_rewards_on_current_order()
        # If order has coupon the removed all program
        if order.code_promo_program_id:
            applied_programs = order.code_promo_program_id
        # Sort by discount percentage
        for program in applied_programs.sorted('discount_percentage', reverse = True):
            #  If line has no program then apply program
            lines = self._get_paid_order_lines()
            if not lines.filtered(lambda x: not x.coupon_program_ids):
                continue
            values = order._get_reward_line_values(program)
            lines = order.order_line.filtered(lambda line: line.product_id == program.discount_line_product_id)
            if program.reward_type == 'discount' and program.discount_type == 'percentage':
                lines_to_remove = lines
                # Values is what discount lines should really be, lines is what we got in the SO at the moment
                # 1. If values & lines match, we should update the line (or delete it if no qty or price?)
                # 2. If the value is not in the lines, we should add it
                # 3. if the lines contains a tax not in value, we should remove it
                for value in values:
                    value_found = False
                    for line in lines:
                        # Case 1.
                        if not len(set(line.tax_id.mapped('id')).symmetric_difference(set([v[1] for v in value['tax_id']]))):
                            value_found = True
                            # Working on Case 3.
                            lines_to_remove -= line
                            lines_to_remove += update_line(order, line, value)
                            continue
                    # Case 2.
                    if not value_found:
                        order.write({'order_line': [(0, False, value)]})
                # Case 3.
                # Do no allow to unlink the existing discount as the above two cases are not triggered.
                if values:
                    lines_to_remove.unlink()
            else:
                update_line(order, lines, values[0]).unlink()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    coupon_program_ids = fields.Many2many('coupon.program', string='Promotions Applied')
    promotional_discount = fields.Float(string='Promotional Discount')
    discounted_total = fields.Float(string='Discounted Total')
