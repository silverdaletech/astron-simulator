# -*- coding: utf-8 -*-

{
    'name': "SME User Log Details",

    'summary': "Login User Details & IP Address & MAC Address",
    
    'description': """
        This module records login information of users
        This will also provide functionality of ending users session.
        This will also add feature of auto session timeout of logged in users.
        This module provides the following feature.
            1: Records login information of users, IP, datetime etc
            2: Allow admin user to user sessions.
            3: Auto session timeout.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['sd_base_setup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/login_user_views.xml',
        'views/login_user_report_template.xml',
        'views/login_user_report_wizard.xml',
        'views/user_report.xml',
        'views/user_view.xml',
        'views/res_config_view.xml',
        'wizard/confirm_wizard.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
