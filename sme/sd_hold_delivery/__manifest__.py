# -*- coding: utf-8 -*-
{
    'name': "SME Hold Delivery",

    'summary': "This Module will allow to Hold Delivery Orders without Payments.",

    'description': """
       1: This Module will allow to Hold Delivery Orders without Payments.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock','sd_sale','sd_base_setup'],

    'data': [
        'views/view_sale_order.xml',
        'views/view_payment_term.xml',
        'views/view_stock_picking.xml',
    ],

    "application": True,
    "installable": True,
    "auto_install": False,
}
