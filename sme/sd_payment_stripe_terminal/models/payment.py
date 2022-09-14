import logging
import pdb

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare
import requests
# import xmltodict
# import hashlib
import stripe

_logger = logging.getLogger(__name__)


class AcquirerStripeTerminal(models.Model):
    """add field for stripe terminal"""
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('stripe_terminal', 'Stripe Terminal')],ondelete={'stripe_terminal': 'set default'})
    pos_stripe_api_key = fields.Char(string="Stripe API key",help='Use when connecting to Stripe Payment terminal: https://stripe.com/docs/terminal/',copy=False)
    is_simulated_reader = fields.Boolean(string="Stripe Test Mode", copy=False)
    registration_code = fields.Char(string="Registration Code", copy=False)
    location_id = fields.Char(string="Location ID", copy=False)
    device_name = fields.Char(string="Device Name")
    auto_download = fields.Boolean(string="Auto Download (Invoice)",  )
    enable_payment = fields.Boolean(string="Enable Stripe terminal Payment option on Invoice and Quotation",  )

    def action_is_key(self, orderId, invoice, link_url):
        """Test the stripe connection to proceed transactions"""
        error = {}
        type = None
        order = None
        try:
            payment_method = self.env['payment.acquirer'].search([('id', '=', int(self.id))])
            if invoice:
                invoice = invoice.split('/')

                if len(invoice) > 2:
                    invoice_id = [value for value in invoice[3].split('?') if value.isdigit()]
                    if len(invoice_id) > 0:
                        if 'orders' in invoice:
                            type = 'order'
                            order = self.env['sale.order'].sudo().search([('id', '=', int(invoice_id[0]))])
                            
                        elif 'invoice' in invoice:
                            type = 'invoice'
                            order = self.env['account.move'].sudo().search([('id', '=', int(invoice_id[0]))])
                            
            values = {}
            # if order and not order.stripe_terminal_tx_nid:
            if order:
                values.update({'error': False,
                               'order': order.id,
                               'acquirer_id': payment_method.id,
                               'order_type': type})
                stripe.api_key = str(payment_method.pos_stripe_api_key)
                valid = stripe.terminal.ConnectionToken.create()
                if valid:
                    return self.env['ir.ui.view'].sudo()._render_template( "sd_payment_stripe_terminal.stripe_terminal_template_modal", values)
            else:
                    error.update({
                                  'order_type': type ,
                                  'error': True,
                                  'order': order.id if order else None,
                                  'message': 'Issue on Odoo Quotation/Invoice.'})
                    return error

        except Exception as ex:
            error.update({'error': True,
                          'order_type': type ,
                          'order': order.id if order else None,
                          'message': ex})
            return error

    def waiting_template_message(self,invoice,inv_type):
        """Test the stripe connection to proceed transactions"""
        values = {}
        type = None

        if inv_type and invoice:
            values.update({'error': False,
                           'order': invoice,
                           'acquirer_id':self.id,
                          'order_type': inv_type})

        return self.env['ir.ui.view'].sudo()._render_template( "sd_payment_stripe_terminal.stripe_terminal_template_modal_waiting_card", values)

    def action_register_device(self):
        """test the stripe connection from odoo"""
        payment_method = self.env['payment.acquirer'].search([('id', '=', int(self.id))])
        for rec in payment_method:
            stripe.api_key = rec.pos_stripe_api_key
            try:
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

    def stripe_terminal_test(self):
        """test the stripe connection from odoo"""
        try:
            payment_method = self.env['payment.acquirer'].search([('id', '=', int(self.id))])
            stripe.api_key = str(payment_method.pos_stripe_api_key)
            valid = stripe.terminal.ConnectionToken.create()
            if valid:
                raise ValueError('Successfully connected..')
        except Exception as ex:
            raise  ValidationError(ex)

    @api.model
    def stripe_terminal_s2s_form_process(self, data):
        """overwrite to create payment token for stripe"""
        payment_token = self.env['payment.token'].sudo().create({
            'name':data.get('partner_id')+data.get('acquirer_id'),
            'verified': True,
            'acquirer_id': data.get('acquirer_id'),
            'partner_id': data.get('partner_id')
        })
        return payment_token


class TransactionStripeTerminal(models.Model):
    _inherit = 'payment.transaction'

    stripe_terminal_tx_nid = fields.Char('Transaction ID')
    stripe_terminal_tx_currency = fields.Char('Transaction Currency')
    card_number = fields.Char('Card Number')
    card_type = fields.Char('Card Type')
    card_holder = fields.Char('Card Holder')
    stripe_charge_id = fields.Char(string="Stripe Charge ID:", required=False, )
    is_interac = fields.Boolean(string="Is Interac Card", defualt=False)

    @api.model
    def _stripe_terminal_form_get_tx_from_data(self, data):
        """overwrite for stripe terminal transaction"""
        _logger.info("********************form data=%r", data)
        reference, amount = data.get('reference'), data.get('amount')

        if not reference:
            error_msg = 'Stripe Terminal: received data with missing reference (%s) or acquirer_reference (%s) or ' \
                        'Amount (%s)' % (
                reference, amount)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % ((reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _stripe_terminal_form_get_invalid_parameters(self, data):
        """overwrite to check stripe transaction validation"""
        invalid_parameters = []
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _stripe_terminal_form_validate(self, tree):
        """overwrite to validate stripe payment """
        for tran in self:
            tran.ensure_one()
            if tran.state  in ("done", "authorized"):
                _logger.info('Stripe Terminal: trying to validate an already validated tx (ref %s)', tran.reference)
                return True

            status = tree.get('status')
            tx_id = tree.get('acquirer_reference')
            # tx_secret = tree.get("client_secret")
            vals = {
                "date": fields.datetime.now(),
                "acquirer_reference": tx_id,
            }
            if status == 'done':
                tran.write(vals)
                tran._set_transaction_done()
                # tran._set_transaction_authorized()
                tran.type = 'form_save'
                tran.execute_callback()
                if tran.type == 'form_save':
                    s2s_data = {
                        'acquirer_ref': tree.get('acquirer_reference'),
                        'acquirer_id': tran.acquirer_id.id,
                        'partner_id': tran.partner_id.id
                    }
                    token = tran.acquirer_id.stripe_terminal_s2s_form_process(s2s_data)
                    tran.payment_token_id = token.id
                if tran.payment_token_id:
                    tran.payment_token_id.verified = True
                tran._post_process_after_done()
                return True
            if status in ('processing', 'requires_action', 'pending_submission'):
                tran.write(vals)
                tran._set_transaction_pending()
                return True
            if status == 'requires_payment_method':
                tran._set_transaction_cancel()
                return False
            else:
                error = 'Transection is faild due to some issues'
                tran._set_transaction_error(error)
                return False

    def _invoice_sale_orders(self):
        res = super(TransactionStripeTerminal, self)._invoice_sale_orders()
        for invoice in self.sale_order_ids.invoice_ids:
            if not invoice.stripe_terminal_tx_nid:
                invoice.stripe_terminal_tx_nid = self.sale_order_ids.stripe_terminal_tx_nid
                break
        return res

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Find the transaction based on the feedback data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the acquirer
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'stripe_terminal':
            return tx

        reference = data.get('reference')
        tx = self.search([('reference', '=', reference), ('provider', '=', 'stripe_terminal')])
        if not tx:
            raise ValidationError(
                "Authorize.Net: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Authorize data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        super()._process_feedback_data(data)
        if self.provider != 'stripe_terminal':
            return

        response_content = data.get('acquirer_reference')

        self.acquirer_reference =data.get('acquirer_reference')
        status_code = data.get('status')
        if status_code == 'done':
            self._set_done()
            if self.tokenize and not self.token_id:
                self.stripe_terminal_s2s_form_process()
        elif status_code == 'cancel':  # Declined
            self._set_canceled()
        elif status_code == 'fail':  # Held for Review
            self._set_pending()
        else:  # Error / Unknown code
            error_code = response_content.get('x_response_reason_text')
            _logger.info(
                "received data with invalid status code %s and error code %s",
                status_code, error_code
            )
            self._set_error(
                "Authorize.Net: " + _(
                    "Received data with status code \"%(status)s\" and error code \"%(error)s\"",
                    status=status_code, error=error_code
                )
            )

    def _send_payment_request(self):
        """ Override of payment to simulate a payment request.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_payment_request()
        if self.provider != 'stripe_terminal':
            return

        # The payment request response would normally transit through the controller but in the end,
        # all that interests us is the reference. To avoid making a localhost request, we bypass the
        # controller and handle the fake feedback data directly.
        self._handle_feedback_data('test', {'reference': self.reference})


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    stripe_terminal_tx_nid = fields.Char('Stripe Transaction ID')

    def copy(self,default=None):
        """remove value from stripe terminal transaction id when duplication the recode"""
        default = default or {}
        if self.stripe_terminal_tx_nid:
            default['stripe_terminal_tx_nid'] = None
        return super(SaleOrder, self).copy(default=default)

    def has_to_be_paid(self, include_draft=False):
        res = super(SaleOrder, self).has_to_be_paid(include_draft)
        acquirer = self.env['payment.acquirer'].search([('provider', '=', 'stripe_terminal')], limit=1)
        automatic_invoice = self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice')
        if not res and  acquirer and acquirer.pos_stripe_api_key and acquirer.enable_payment and self.state in ['draft','sent']:
            if self.require_signature and self.state=='draft':
                self.state = 'sent'

            if not automatic_invoice:
                self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', True)
            return True
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    stripe_terminal_tx_nid = fields.Char('Stripe Transaction ID')
    enable_refund_option = fields.Boolean(string="Enable Strip Terminal refund", )
    # enable_stripe_payment = fields.Boolean(string="Enable Payment Option",  )
    is_stripe_terminal = fields.Boolean(string="Is Terminal Enable",  )

    def copy(self, default=None):
        """remove value from stripe terminal transaction id when duplication the recode"""
        self.ensure_one()
        default = default or {}
        if self.stripe_terminal_tx_nid:
            default['stripe_terminal_tx_nid'] = None
        default['enable_refund_option'] = False

        return super(AccountMove, self).copy(default=default)

    def _get_reconciled_info_JSON_values(self):
        """overwrrite to add stripe payment detail in invoice report"""
        res = super(AccountMove, self)._get_reconciled_info_JSON_values()

        for rec in res:
            payment = self.env['account.payment'].browse(rec.get('account_payment_id', 0))
            if payment and payment.payment_transaction_id and payment.payment_transaction_id.card_number:
                rec['card_number'] = payment.payment_transaction_id.card_number
                rec['card_type'] = payment.payment_transaction_id.card_type
                rec['stripe'] = True

            else:
                rec['stripe'] = False

        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        acquirer = self.env['payment.acquirer'].search([('provider', '=', 'stripe_terminal')], limit=1)
        if acquirer and acquirer.pos_stripe_api_key and acquirer.enable_payment:
            self.is_stripe_terminal = True
        if self.reversed_entry_id:
            ref = None
            payments = None
            if self.reversed_entry_id.invoice_origin:
                ref = self.reversed_entry_id.invoice_origin
            elif self.reversed_entry_id.payment_reference:
                ref = self.reversed_entry_id.payment_reference
            if ref:
                transaction = self.env['payment.transaction'].search([('invoice_ids','=',self.reversed_entry_id.id),('provider','=','stripe_terminal')],limit=1)

                if transaction  and transaction.is_interac:
                    self.enable_refund_option = True

        return res

    def preview_invoice(self):
        res = super(AccountMove, self).preview_invoice()
        acquirer = self.env['payment.acquirer'].search([('provider', '=', 'stripe_terminal')], limit=1)
        if acquirer and acquirer.pos_stripe_api_key and acquirer.enable_payment:
            if self.state == 'draft':
                self.state = 'posted'
            self.is_stripe_terminal = True
        return res





class AccountMoveRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    stripe_charge_id = fields.Char(string="Stripe Charge ID:", required=False, )
    is_stripe = fields.Boolean(string="Is Stripe")

    def _create_payments(self):
    
        if self.payment_method_code == 'STout':

            if self.line_ids.move_id.reversed_entry_id.stripe_terminal_tx_nid:
                try:
                    payment_method = self.env['payment.acquirer'].search([('provider', 'ilike', 'stripe_terminal')])
                    if payment_method:
                        stripe.api_key = str(payment_method.pos_stripe_api_key)

                    rslt = stripe.Refund.create(payment_intent=self.line_ids.move_id.reversed_entry_id.stripe_terminal_tx_nid,
                                                amount=int(self.amount * 100))

                    self.line_ids.move_id.stripe_terminal_tx_nid = rslt.id
                    self.line_ids.move_id.payment_reference = rslt.id

                    return super(AccountMoveRegister, self)._create_payments()


                except Exception as ex:
                    raise ValidationError(ex)

            else:
                raise ValidationError("The payment against this invoice haven't done through stripe. Please choose other payment methods")
        else:
            return super(AccountMoveRegister, self)._create_payments()


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"
    _description = "Payment Methods"

    def _get_payment_method_information(self): 
        res = super(AccountPaymentMethod, self)._get_payment_method_information()
        res['STout']= {'mode': 'multi', 'domain': [('type', 'in', ('bank', 'cash'))]}
        res['stripe_terminal']= {'mode': 'multi', 'domain': [('type', 'in', ('bank', 'cash'))]}

        return res



