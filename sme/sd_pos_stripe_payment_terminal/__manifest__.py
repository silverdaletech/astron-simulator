# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'SME POS Stripe Payment Terminal',
    'summary': 'Integrate your POS with Stripe payment terminal',
    'description': """
        Integrate your POS with Stripe payment terminal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Sales/Point of Sale',

    'external_dependencies': {
        'python': ['stripe'],
    },

    'depends': ['sd_pos_payment_terminal'],

    'data': [
        'views/pos_config_views.xml',
        'views/pos_payment_method_views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'sd_pos_stripe_payment_terminal/static/**/*',
        ],
        'web.assets_qweb': [

            "sd_pos_stripe_payment_terminal/static/src/xml/load_stripe_asset.xml",

        ],
    },

    'installable': True,
    'auto_install': False,
    'application': False,
}
