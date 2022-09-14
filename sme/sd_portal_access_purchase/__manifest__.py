# -*- coding: utf-8 -*-
{
    'name': "SME Portal Access: Purchase App",

    'summary': "Portal Access: Enable of Disable contact to access Purchase Order/Quotation on Portal",

    'description': """
        Portal Access: Enable of Disable contact to access Purchase Order/Quotation on Portal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Purchase',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_contact', 'purchase'],

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
