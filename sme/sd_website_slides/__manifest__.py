# -*- coding: utf-8 -*-
{
    'name': "SME eLearning",

    'summary': "Enable eLearning features develop by Silverdale.",

    'description': """
        1: Vimeo Videos - eLearning Platform
        2: eLearning Publish/UnPublish
        3: Invite multiple attendees
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'eLearning',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'website_slides'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

