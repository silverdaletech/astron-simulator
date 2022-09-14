# -*- coding: utf-8 -*-
{
    'name': "Add Remaining Delivery Cost",

    'summary': "Feature of Add Remaining Delivery Cost.",

    'description': """
        1: Will Add Remaining Delivery Cost
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Delivery',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'delivery','sd_base_setup'
    ],

    # always loaded
    'data': [
        'wizard/choose_delivery_carrier_views.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
