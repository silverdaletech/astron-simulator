# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Square Payment Terminal',
    'summary': 'Integrate your POS with Square payment terminal',
    'description': 'Integrate your POS with Square payment terminal',

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",

    'category': 'Point of Sale',
    'version': '2208',
    'license': 'OPL-1',

    'depends': ['sd_pos_payment_terminal'],

    'data': [
        'security/ir.model.access.csv',
        # 'views/pos_config_views.xml',
        'views/pos_payment_method_views.xml',
        'views/square_device_code_views.xml',
        'wizard/message_view.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'sd_pos_square_payment_terminal/static/**/*',
        ],

    },

    'installable': True,
    'auto_install': True,
    'application': True,
}
