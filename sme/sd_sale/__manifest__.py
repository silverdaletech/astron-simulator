# -*- coding: utf-8 -*-
{
    'name': "SME Sale",

    'summary': "This will help in sales for Enabling Features develop by Silverdale.",

    'description': """
        1: Complete Sale Order
        2: Signed Sale order
        3: Project Description from SO
        4: Sale price change
        5: MRP Status
        6: Credit Management
        7: Sale Default Analytic Rules
        8: Sale Agreements
        9: Silverdale Sale Commission
        10: Coupons and Promotions
        11: Sales on CRM
        12: Stripe Terminal For Invoice/Quotation
        13: Silverdale Authoriz.net
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'sale', 'sale_management'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/view_res_config_setting.xml',
        'views/view_sale_order.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
