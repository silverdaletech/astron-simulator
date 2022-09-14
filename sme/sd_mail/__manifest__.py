# -*- coding: utf-8 -*-
{
    'name': "SME Mail",

    'summary': "Enabling mail features develop by Silverdale.",

    'description': """
        1: Send Message Composer
        2: Mail Extension
        3: BCC Email
        4: Company Based Notifications
        5: Activity For Multiple Users
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Productivity/Discuss',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'mail'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

