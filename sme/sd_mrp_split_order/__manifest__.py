# -*- coding: utf-8 -*-
{
    'name': "SME MRP Split Order",

    'summary': "Split MRP order in multiple separate orders",

    'description': """
        1: Split MRP order in multiple separate orders
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Manufacturing',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp','sd_base_setup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/view_res_config_setting.xml',
        'wizard/split_order_wizard.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
