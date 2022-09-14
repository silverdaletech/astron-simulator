# -*- coding: utf-8 -*-
{
    'name': "SME Documents",

    'summary': "Customization related to Documents",

    'description': """
        1: Functionality to show model and record on document view to attach that document against then record.
        2: Functionality to allow/disallow a Portal User from seeing module data on the Portal.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdale.com",
    'license': 'OPL-1',
    
    'version': '2207',
    'category': 'Documents',

    # any module necessary for this one to work correctly
    'depends': ['sd_base_setup', 'documents'],

    # always loaded
    'data': [
        "views/res_config_setting.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sd_document/static/src/js/documentsinspector.js',
            'sd_document/static/src/js/views_maxin.js'
        ],
        'web.assets_qweb': [
            'sd_document/static/src/xml/documents_inspector.xml',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
