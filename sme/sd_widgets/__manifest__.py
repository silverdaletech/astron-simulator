# -*- coding: utf-8 -*-
{
    'name': "SME Widgets",
    'summary': "SME widgets",
    'description': """
        1: Related field widget.
        2: Kiosk Numpad Widget.
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2206',
    'category': 'Widgets',
    'depends': ['web', 'base', ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'sd_widgets/static/src/css/kioskboard.css',

            'sd_widgets/static/src/js/kioskboard.js',
            'sd_widgets/static/src/js/basic_fields.js',
            'sd_widgets/static/src/js/field_registry.js',
            'sd_widgets/static/src/js/abstract_field.js',
            'sd_widgets/static/src/js/domain_selector_extend.js',
            'sd_widgets/static/src/js/basic_fields_extend.js',
            'sd_widgets/static/src/js/domain_selector_dialog_extend.js',
        ],
        'web.assets_qweb': [
            'sd_widgets/static/src/xml/base_extend.xml',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
