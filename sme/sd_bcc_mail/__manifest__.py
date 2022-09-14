# -*- coding: utf-8 -*-
{
    'name': "SME BCC Email",

    'summary': "Email BCC feature on Email Template",

    'description': """
       1:Email BCC feature available on Email template.
       2:Email BCC feature available on send by Email Wizard
       3:Display BCC Email in chatter
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Tools',

    'depends': [
        'base', 'mail','sd_base_setup'
    ],

    'data': [
        'views/mail_template_views.xml',
        'views/mail_mail_views.xml',
        'wizard/message_compose_inherit.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'sd_bcc_mail/static/src/js/sd_message_inherit.js',
        ],
        'web.assets_qweb': [
            '/sd_bcc_mail/static/src/xml/sd_templates_inherit.xml',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,

}
