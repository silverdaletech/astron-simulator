# -*- coding: utf-8 -*-
{
    'name': "SME Manufacturing",

    'summary': "Enable Manufacturing features develop by Silverdale.",

    'description': """
        1: MRP Split Order
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Manufacturing',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'mrp'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

