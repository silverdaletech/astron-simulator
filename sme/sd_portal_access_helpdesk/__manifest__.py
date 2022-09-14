# -*- coding: utf-8 -*-
{
    'name': "SME Portal Access: Helpdesk App",

    'summary': "Portal Access: Enable of Disable user to access Helpdesk ticket on Portal",

    'description': """
        Portal Access: Enable of Disable user to access Helpdesk Tickets on Portal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Helpdesk',

    # any module necessary for this one to work correctly
    'depends': ['base','sd_contact','helpdesk','portal'],

    # always loaded
    'data': [

        'views/views.xml',
        'views/templates.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',

}
