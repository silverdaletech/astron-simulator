# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI
from odoo.addons.payment import utils as payment_utils
_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    is_invoice_address = fields.Boolean(string="Use Invoice Address For Payment")


def _prepare_authorization_transaction_request_modify(self, transaction_type, tx_data, tx):
    # The billTo parameter is required for new ACH transactions (transactions without a payment.token),
    # but is not allowed for transactions with a payment.token.
    bill_to = {}
    _logger.info('Calling Transaction Request')
    _logger.info('Partner Address============ {}'.format(tx.partner_address))
    _logger.info('Partner Address============ {}'.format(tx_data))

    _logger.info('Calling Transaction Request')

    if 'profile' not in tx_data:
        if tx.sale_order_ids and tx.acquirer_id.is_invoice_address:
            _logger.info('******&&Inside Invoice address&&******')
            invoice_address = tx.sale_order_ids.partner_invoice_id
            if invoice_address:
                _logger.info('Invoice Address============ {}'.format(invoice_address.street))
                split_name = payment_utils.split_partner_name(tx.partner_name)
                partner_name = (invoice_address.name or "")[:50]  # max length defined by the Authorize API
                bill_to = {
                    'billTo': {
                        'firstName': split_name[0],
                        'lastName': split_name[1],  # lastName is always required
                        'company': partner_name if invoice_address.is_company else '',
                        'address': invoice_address.street,
                        'city': invoice_address.city,
                        'state': invoice_address.state_id.name or '',
                        'zip': invoice_address.zip,
                        'country': invoice_address.country_id.name or '',
                    }
                }
            else:
                split_name = payment_utils.split_partner_name(tx.partner_name)
                partner_name = (tx.partner_name or "")[:50]  # max length defined by the Authorize API
                bill_to = {
                    'billTo': {
                        'firstName': '' if tx.partner_id.is_company else split_name[0],
                        'lastName': split_name[1],  # lastName is always required
                        'company': partner_name if tx.partner_id.is_company else '',
                        'address': tx.partner_address,
                        'city': tx.partner_city,
                        'state': tx.partner_state_id.name or '',
                        'zip': tx.partner_zip,
                        'country': tx.partner_country_id.name or '',
                    }
                }
        else:
            split_name = payment_utils.split_partner_name(tx.partner_name)
            partner_name = (tx.partner_name or "")[:50]  # max length defined by the Authorize API
            bill_to = {
                'billTo': {
                    'firstName': '' if tx.partner_id.is_company else split_name[0],
                    'lastName': split_name[1],  # lastName is always required
                    'company': partner_name if tx.partner_id.is_company else '',
                    'address': tx.partner_address,
                    'city': tx.partner_city,
                    'state': tx.partner_state_id.name or '',
                    'zip': tx.partner_zip,
                    'country': tx.partner_country_id.name or '',
                }
            }

    # These keys have to be in the order defined in
    # https://apitest.authorize.net/xml/v1/schema/AnetApiSchema.xsd
    _logger.info('************ bill to============ {}'.format(bill_to))
    return {
        'transactionRequest': {
            'transactionType': transaction_type,
            'amount': str(tx.amount),
            **tx_data,
            'order': {
                'invoiceNumber': tx.reference[:20],
                'description': tx.reference[:255],
            },
            'customer': {
                'email': tx.partner_email or '',
            },
            **bill_to,
            'customerIP': payment_utils.get_customer_ip_address(),
        }
    }


AuthorizeAPI._prepare_authorization_transaction_request = _prepare_authorization_transaction_request_modify


