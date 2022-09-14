# -*- coding: utf-8 -*-
{
    'name': "SME Coupons and Promotions",

    'summary': "Coupons and Promotions amounts in sale order lines.",

    'description': """
    
        When a Promotion is applied on an order line then Odoo adds a new line for the promotional 
        discount that applies to the order. With this behavior, there is no way to figure out the 
        total amount for each line in the sale order in it's discount form.
        In this module, we have added the functionality which let user see the total discounted amount 
        and promotion amount per line on sale order.
    
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_coupon'],

    # always loaded
    'data': [
        'views/sale_order_views.xml',
        'views/res_config_setting.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
