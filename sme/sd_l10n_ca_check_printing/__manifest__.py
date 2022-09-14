# -*- coding: utf-8 -*-
{
    'name': "SME CA Checks Layout",

    'summary': "CA Checks Layout Extension.",

    'description': """
        This module allows to print your reconciled payments on pre-printed check paper.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Accounting/Accounting',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'l10n_ca_check_printing', 'sd_account_check_printing'],

    # always loaded
    'data': [
        'report/print_check_ext.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
