# -*- coding: utf-8 -*-
{
    'name': "SME Credit Management",

    'summary': "Credit Management System",

    'description': """
       1: Allow to set credit Limit on partners
       2: Hold Sale order if exceed credit limit
       3: Hold Delivery if exceed credit limit
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Sale',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'sale', 'stock', 'sd_sale', 'sd_base_setup'
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/view_res_group.xml',
        'views/view_res_partner.xml',
        'views/view_sale_order.xml',
        'wizard/partner_credit_limit_view_warning.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
