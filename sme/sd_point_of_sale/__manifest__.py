# -*- coding: utf-8 -*-
{
    'name': "SME Point of Sales",

    'summary': "Enable Point of Sales features develop by Silverdale.",

    'description': """
        1: Point of Sale Extra Features
        2: POS Payment Terminal Base
        3: POS Stripe Payment Terminal
        4: POS Sale Subscription
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales/Point of Sale',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'point_of_sale'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

