# -*- coding: utf-8 -*-
{
    'name': "Account PDF Ext",

    'summary': "Invoice Report Extend For Reliance",

    'description': """ 
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '15.0',
    'category': 'Account',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'sale', 'account'
    ],

    # always loaded
    'data': [
        'report/report_invoice_document_inherit.xml',
    ],

    "uninstall_hook": "uninstall_hook",
    'application': True,
    'installable': True,
    'auto_install': False,
}
