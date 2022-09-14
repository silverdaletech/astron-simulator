# -*- coding: utf-8 -*-
{
    'name': "SME CRM",

    'summary': "Silverdale Module Extension for Odoo CRM module.",

    'description': """
        1.This will help in sales for Enabling Features develop by Silverdale
        2.Functionality of Auto email on every lead/opportunity creation.
        3.Functionality of Auto activity creation on every lead/opportunity creation.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': "Other proprietary",
    'version': '2207',
    'category': 'CRM',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        'views/crm_mail_template.xml',
        'views/view_res_config_setting.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}

