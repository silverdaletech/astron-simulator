# coding: utf-8
import json
import logging
import pprint
import random
import requests
import string
from werkzeug.exceptions import Forbidden
import stripe
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    """Interit to add fields for stripe payment terminals """
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('sd_pos_stripe_payment_terminal', 'Stripe Payment Terminal')]

    pos_stripe_api_key = fields.Char(string="Stripe API key", help='Used when connecting to Stripe Payment terminal: https://stripe.com/docs/keys', copy=False)
    is_simulated_reader = fields.Boolean(string="Stripe Test Mode", copy=False)
    registration_code = fields.Char(string="Registration Code", copy=False)
    location_id = fields.Char(string="Location ID", copy=False)
    device_name = fields.Char(string="Device Name")

    def pos_credential_test(self):
        """Test the stripe connection to proceed transactions"""
        try:
            payment_method = self.env['pos.payment.method'].search([('id', '=', int(self.id))])
            stripe.api_key = str(payment_method.pos_stripe_api_key)
            valid = stripe.terminal.ConnectionToken.create()
            if valid:
                return "valid_key"
        except:
            return "invalid_key"

    def action_register_device(self):
        """Register the stripe terminal device with stripe account """
        try:
            for rec in self:
                stripe.api_key = rec.pos_stripe_api_key
                register_code = rec.registration_code
                location_id = rec.location_id
                label = rec.device_name
                registered_device = stripe.terminal.Reader.create(
                    registration_code=f'{register_code}',
                    label=label,
                    location=f'{location_id}',
                )
                print('message', registered_device)
                _logger.info('Stripe device has registered : ', registered_device)

        except Exception as ex:
                raise ValidationError(ex)


class PosPayment(models.Model):
    """Interit to add fields for stripe payment terminals """
    _inherit = "pos.payment"

    stripe_intend_payment_id = fields.Char(string="Stripe Intend Payment ID", required=False, )
    refunded_id = fields.Char(string="Stripe Refunded ID", required=False, )
    last_digits = fields.Char(string="Card Number", required=False, )
    charge_id = fields.Char(string="Stripe Charge ID:", required=False, )


class PosOrder(models.Model):
    _inherit = "pos.order"
    stripe_intend_payment_id = fields.Char(string="Stripe Intend Payment ID", required=False, )

    def _payment_fields(self, order, ui_paymentline):
        rec = super(PosOrder, self)._payment_fields( order, ui_paymentline)
        rec['last_digits'] = ui_paymentline.get('last_digits',False)
        rec['charge_id'] = ui_paymentline.get('charge_id',False)
        rec['refunded_id'] = ui_paymentline.get('refunded_id',False)
        rec['stripe_intend_payment_id'] = ui_paymentline.get('stripe_intend_payment_id',False)
        return  rec


class PosMakePaymentInh(models.TransientModel):
    _inherit = 'pos.make.payment'

    def check(self):

        order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        refunded_order = self.env['pos.order'].search([('name', '=', order.name.split(' ')[0])])
        if self.payment_method_id.use_payment_terminal == 'sd_pos_stripe_payment_terminal':
            if self.payment_method_id.pos_stripe_api_key:
                if refunded_order:
                    for payment in refunded_order.payment_ids:
                        if payment.transaction_id and not payment.refunded_id:
                            try:
                                stripe.api_key = self.payment_method_id.pos_stripe_api_key
                                rslt = stripe.Refund.create(payment_intent=payment.transaction_id,
                                                            amount=int(-(self.amount) * 100))
                                _logger.info('Successfully refunded  payment with details {}'.format(rslt))

                                res = super(PosMakePaymentInh, self).check()

                                # order.payment_ids[0].transaction_id = rslt.id
                                order.payment_ids[0].refunded_id = rslt.id

                                return res

                            except Exception as ex:
                                raise ValidationError('Stripe Terminal Error: {}'.format(ex))

                        else:
                            raise ValidationError('The Payment against this order is not done through stripe '
                                                  'terminal so you can not refund it through this payment method.'
                                                  ' Please select other payment method.')
                else:
                    raise ValidationError('Odoo Error... Please try to refund with other payment method')
            else:
                raise ValidationError(
                    'No API key provided. Please set stripe API key for selected payment method: {}'.format(
                        self.payment_method_id.name))

        else:
            res = super(PosMakePaymentInh, self).check()
            return res
