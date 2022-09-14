# -*- coding: utf-8 -*-
{
    'name': "SME Account",
    'summary': "Enable Account features develop by Silverdale.",

    'description': """
        1: Silverdale Check Printing Base
        2: Silverdale CA Checks Layout
        3: Silverdale US Checks Layout
        4: SME Equipment to Asset
    """,

    "author": "Silverdale",
    "website": "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Accounting',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'account'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
