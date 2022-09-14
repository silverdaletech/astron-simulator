# -*- coding: utf-8 -*-
{
    'name': "SME Sale Order Sign",
    'summary': "Add signed status in sale order",

    'description': """
        1:Add signed status in sale order
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales',

    # any module necessary for  one to work correctly
    'depends': ['base', 'sd_sale','sd_base_setup'],

    'data': [
        'views/sale_order_view.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,

}
