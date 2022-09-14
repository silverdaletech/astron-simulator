# -*- coding: utf-8 -*-
{
    'name': "SME Base Setup",

    'summary': "This Module is use for base setup for silverdale modules",

    'description': """
        1: This Module is use for base setup for silverdale modules
        2: Open Email composer from Silverdale Waffle 
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    'category': 'Base',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'base_setup', 'web', 'mail'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/data.xml',
        'data/mail_template_get_help.xml',
        'wizards/message_view.xml',
        'views/view_res_config_setting.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/sd_base_setup/static/lib/js/pyeval.js',
            '/sd_base_setup/static/src/js/sd_status_menu.js',
            '/sd_base_setup/static/src/css/sd_status_menu.css',
        ],
        'web.assets_qweb': [
            '/sd_base_setup/static/src/xml/*.xml',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': True,
}
