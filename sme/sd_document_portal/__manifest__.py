# -*- coding: utf-8 -*-
{
    'name': "Documents On Portal",

    'summary': """
        User contact documents on portal
    """,

    'description': """

    """,

    'author': "Silverdale",
    'website': "https://www.silverdale.com",
    'license': 'Other proprietary',
    
    'version': '2207',
    'category': 'Customizations',

    # any module necessary for this one to work correctly
    'depends': ['base', 'documents', 'portal', 'sd_document'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/res_config_setting_view.xml',
        'views/portal_template.xml',
        'views/res_config_setting.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'sd_document_portal/static/src/js/documents_view_mixin.js',
            'sd_document_portal/static/src/js/documents_inspector.js',
            'sd_document_portal/static/src/js/documents_controller_mixin.js',
        ]
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}
