# -*- coding: utf-8 -*-
{
    "name": "SME Account Mail Extension",

    "summary": "Email 'From' Feature on Invoice",

    "description": """
        Feature to show and Change 'From' Email on Invoice Mail Wizard.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2209',
    "category": "mail",

    "depends": [
        'sd_mail_ext', 'account', 'base'
    ],

    # always loaded
    'data': [
        "wizards/account_invoice_send.xml",
        ],

    "application": False,
    "installable": True,
    "auto_install": False,
}
