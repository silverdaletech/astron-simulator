# -*- coding: utf-8 -*-
{
    'name': "SME Prevent Negative Stock",

    'summary': "Disallow negative Inventory Levels",

    'description': """
        Disallow negative Inventory Levels
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Inventory',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'stock', 'sd_stock'
    ],

    # always loaded
    'data': [
        'views/stock_location_views.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}
