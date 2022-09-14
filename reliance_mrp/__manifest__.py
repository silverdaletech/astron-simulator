# -*- coding: utf-8 -*-
{
    'name': "Reliance MRP",

    'summary': "Customized module for Reliance MRP/LOT",

    'description': """ 
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '15.0.1',
    'category': 'Manufacturing',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'mrp', 'stock'
    ],

    # always loaded
    'data': [
        'views/product_template_view.xml',
        'views/stock_move.xml',
        'views/stock_production_lot.xml',
        # 'wizards/mrp_product_produce_wizard.xml'  ,
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
