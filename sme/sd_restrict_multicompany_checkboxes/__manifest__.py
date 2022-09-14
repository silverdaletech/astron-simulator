# -*- coding: utf-8 -*-
{
    'name': "SME Restrict Multi-Company Checkboxes",

    'summary': "Restrict Multi-company Checkboxes based on user group",

    'description': """
        Add restrictions on multi-company checkboxes inside company selector on the basis of a user group
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Web',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'security/security.xml',
    ],

    'assets': {
        'web.assets_qweb': [
            'sd_restrict_multicompany_checkboxes/static/src/**/*.xml'
        ],
        'web.assets_backend': [
            'sd_restrict_multicompany_checkboxes/static/src/webclient/switch_company_menu/switch_company_menu_ext.js',
        ]
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}
