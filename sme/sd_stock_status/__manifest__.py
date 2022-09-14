# -*- coding: utf-8 -*-
{
    'name': "SME Stock Status",

    'summary': "This will add delivery status on SO",

    'description': """
        1: will add delivery status on SO
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'sd_sale', 'sd_stock'],

    'data': [
        # 'security/security.xml',
        'views/sale_order_view.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,

}
