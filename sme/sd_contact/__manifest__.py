# -*- coding: utf-8 -*-
{
    'name': "SME Contact APP",

    'summary': "Add Options on contact form to access the odoo modules records on portal .",

    'description': """
        1: USPS Address Validation
        2: Partner first name and last name
        3: Partners Pricelist
        4: Enable of Disable user to access Invoices on Portal
        5: Enable of Disable user to access Sale Order/Quotations on Portal
        6: Enable of Disable user to access Helpdesk Tickets on Portal
        7: Enable of Disable user to access Projects on Portal
        8: Enable of Disable user to access Purchases on Portal
        9: Enable of Disable user to access timesheet on Portal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Contact',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'contacts', 'sd_base_setup'
    ],

    # always loaded
    'data': [
        'views/views.xml',
        'views/view_res_config_setting.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': True,

}
