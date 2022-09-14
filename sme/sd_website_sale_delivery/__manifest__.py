# -*- coding: utf-8 -*-
{
    'name': "SME Delivery methods visibility change on website",

    'summary': "Delivery methods visibility change on website",

    'description': """
        T30246
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Website',

    # any module necessary for this one to work correctly
    'depends': ['base','delivery','website_sale_delivery'],

    'data': [
        'views/views.xml',
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
