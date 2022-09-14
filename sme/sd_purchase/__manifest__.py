# -*- coding: utf-8 -*-
{
    'name': "SME Purchase",

    'summary': "Enable Purchase features develop by Silverdale.",

    'description': """
        1: Silverdale Purchase Discounts
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Purchase',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'purchase'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

