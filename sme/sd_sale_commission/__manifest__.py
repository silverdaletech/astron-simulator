# -*- coding: utf-8 -*-
{
    'name': "SME Sale Commission",

    'summary': "This will help in sales for Enabling commission Features develop by Silverdale",

    'description': """
        This will help  in sales for Enabling commission Features develop by Silverdale
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'contacts', 'product', 'sale', 'sale_management'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/view_res_config_setting.xml',
        'views/commission_agent_view.xml',
        'views/sale_commission_record_view.xml',
        'views/sale_commission_settlement_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
        'views/account_view.xml',
        'report/commission_report_views.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
