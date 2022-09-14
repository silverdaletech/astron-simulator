# -*- coding: utf-8 -*-
{
    'name': "SME MRP Status",

    'summary': "MO and invoice status on sale order",

    'description': """
       1: MO status on sale order.
       2: Invoices status on sale order.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'sd_sale_mrp', 'stock','sd_base_setup'],

    'data': [
        # 'security/security.xml',
        'views/sale_order_view.xml',
        'views/mrp_production_view.xml',
        'views/sale_portal_templates.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}

