# -*- coding: utf-8 -*-
{
    'name': "SME Activity For Multiple Users",

    'summary': "This will help in Mail Activity to create activity for multiple users.",

    'description': """
        1:This will help in Mail Activity to create activity for multiple users.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Productivity/Discuss',
    'depends': [
        'base', 'mail', 'sd_base_setup'
    ],
    'data': [
        'views/mail_activity_views.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
