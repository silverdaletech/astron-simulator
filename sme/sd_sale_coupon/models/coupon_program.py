from odoo import api, fields, models, _


class CouponProgram(models.Model):
    _inherit = 'coupon.program'

    def _check_promo_code(self, order, coupon_code):
        """
        Override the message error 'Promotional codes are not cumulative' and allow to update codes,
        if the applied code is not equal to the one that is already applied on the order.
        """
        message = super(CouponProgram, self)._check_promo_code(order, coupon_code)
        if order.promo_code and self.promo_code_usage == 'code_needed' and not (self.promo_code and self.promo_code == order.promo_code):
            message = {}
        return message
