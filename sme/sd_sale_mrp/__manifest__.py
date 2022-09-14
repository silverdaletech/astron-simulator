# -*- coding: utf-8 -*-
{
    'name': "SME MRP",

    'summary': "This will add manufacturing description in SO lines and add in MO notes",

    'description': """
        1: This will add manufacturing description in SO lines and add in MO notes
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'CRM',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_mrp', 'sd_sale','sd_base_setup'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
        'views/view_sale_order.xml',
        'views/view_mrp_production.xml'
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}

