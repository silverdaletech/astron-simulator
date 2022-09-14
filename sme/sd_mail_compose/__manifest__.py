# -*- coding: utf-8 -*-
{
    'name': "SME Send Message Composer",

    'summary': "Open a full composer on the button 'Send a Message'",

    'description': """
        The tool to always open a full composer on the button 'Send a Message' in Chatter.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Discuss',

    "depends": ["mail"],

    'assets': {
        'web.assets_backend': [
            'sd_mail_compose/static/src/components/chatter/chatter.js',
        ]
    },

    "application": True,
    "installable": True,
    "auto_install": False,
}
