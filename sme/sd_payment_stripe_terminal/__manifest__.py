# -*- coding: utf-8 -*-
{
    'name': "SME Stripe Terminal For Invoice/Quotation",
    'summary': "Pay invoices and sale orders through Stripe Payment Terminal.",

    'description': """
        This module will help you to integrate Stripe Terminal Payment with Odoo. 
        With this module, you can pay invoices and sale orders through stripe payment terminal.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'category': 'Payment',
    'version': '2207',
    'depends': ['payment', 'sale_management', 'account_payment'],

    'external_dependencies': {
        'python': ['stripe'],
    },

    'data': [
        'security/ir.model.access.csv',
        'security/stripe_security.xml',
        'views/payment_acquirer.xml',
        'views/account_move_report.xml',
        'views/credit_note_stripe.xml',
        'views/invoice_portal_template.xml',
        'views/payment_views.xml',
        'views/invoice_so_payment.xml',
        'views/sd_payment_stripe_terminal.xml',
        'views/templates.xml',
        'data/payment_acquirer_data.xml',
    ],
 
    'assets': {
        'web.assets_common': [
            'sd_payment_stripe_terminal/static/src/js/stripe_terminal_form.js',
            'sd_payment_stripe_terminal/static/src/js/cancel_payment.js',
            'https://js.stripe.com/terminal/v1/'
        ],
    },

    'images': ['static/description/icon.png'],

    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'auto_install': False,
    'application': False,

}
