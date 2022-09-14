# -*- coding: utf-8 -*-
{
    'name': "SME Sale Order Complete",

    'summary': "Complete sale order after confirm",

    'description': """
        Complete sale order after confirm
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales',

    # any module necessary for this one to work correctly
    'depends': [
        'sd_sale','sd_base_setup'
    ],

    'data': [
        'security/security.xml',
        'views/sale_order_view.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,

}
