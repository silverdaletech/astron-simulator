# -*- coding: utf-8 -*-
{
    'name': "Company Based Notifications",

    'summary': "Company Based User Notifications",

    'description': """
        Separate the user's notifications based on company
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Discuss',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'mail', 'web'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'sd_company_mail/static/src/models/messaging_notification_handler/messaging_notification_handler.js',
        ],
    },

}
