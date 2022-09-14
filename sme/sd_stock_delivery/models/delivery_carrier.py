# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import time

from odoo import api, models, fields, _, tools
from odoo.exceptions import UserError
from odoo.tools import pdf
_logger = logging.getLogger(__name__)


class ProviderFedex(models.Model):
    _inherit = 'delivery.carrier'

    def picking_rate_shipment(self, picking):
        ''' Compute the price of the order shipment

        :param order: record of sale.order
        :return dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
                       # TODO maybe the currency code?
        '''
        self.ensure_one()
        if hasattr(self, '%s_picking_rate_shipment' % self.delivery_type):
            res = getattr(self, '%s_picking_rate_shipment' % self.delivery_type)(picking)
            # apply margin on computed price
            res['price'] = float(res['price']) * (1.0 + (self.margin / 100.0))
            # save the real price in case a free_over rule overide it to 0
            res['carrier_price'] = res['price']
            # free when order is large enough
            order = picking.sale_id
            if res['success'] and self.free_over and order._compute_amount_total_without_delivery() >= self.amount:
                res['warning_message'] = _('The shipping is free since the order amount exceeds %.2f.') % (self.amount)
                res['price'] = 0.0
            return res

    def base_on_rule_picking_rate_shipment(self, picking):
        order = picking.sale_id
        if not order:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this transfer has no sale order.'),
                    'warning_message': _('Error: this transfer has no sale order.')}
        carrier = self._match_address(picking.partner_id)
        if not carrier:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this delivery method is not available for this address.'),
                    'warning_message': False}

        try:
            price_unit = self._get_price_available(order)
        except UserError as e:
            return {'success': False,
                    'price': 0.0,
                    'error_message': e.args[0],
                    'warning_message': False}
        if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
            price_unit = order.company_id.currency_id._convert(
                price_unit, order.pricelist_id.currency_id, order.company_id, order.date_order or fields.Date.today())

        return {'success': True,
                'price': price_unit,
                'error_message': False,
                'warning_message': False}

    def fixed_picking_rate_shipment(self, picking):
        order  = picking.sale_id
        if not order:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this transfer has no sale order.'),
                    'warning_message': _('Error: this transfer has no sale order.')}
        carrier = self._match_address(picking.partner_id)
        if not carrier:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this delivery method is not available for this address.'),
                    'warning_message': False}
        price = self.fixed_price
        company = self.company_id or order.company_id or self.env.company
        if company.currency_id and company.currency_id != order.currency_id:
            price = company.currency_id._convert(price, order.currency_id, company, fields.Date.today())
        return {'success': True,
                'price': price,
                'error_message': False,
                'warning_message': False}