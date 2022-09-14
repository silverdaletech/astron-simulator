# -*- coding: utf-8 -*-
{
    'name': "SME Partners Pricelist",

    'summary': "Check partner associated with pricelist",

    'description': """
        This Module will give the feature on pricelist to check partner associated with pricelist
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Product',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'views/view_product_pricelist.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
