# -*- coding: utf-8 -*-
{
    'name': "SME Check Printing Base",

    'summary': "Check printing basic features extension",

    'description': """
        1:This module extends the basic functionalities to make payments by printing checks
        2:and adding extra stub-lines that are already reconciled payments.
    """,

    "author": "Silverdale",
    "website": "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Accounting/Accounting',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'account_check_printing','sd_base_setup'],

    'application': True,
    'installable': True,
    'auto_install': False,
}
