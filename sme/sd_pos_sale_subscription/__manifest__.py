# -*- coding: utf-8 -*-
{
    "name": "SME POS Sale Subscription",
    "summary": "Create subscription for subscription products from point of sale ",
    "description": """
        1: Create subscription for subscription products from point of sale 
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Point of Sale',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'sale_stock', 'sale_subscription','sd_base_setup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_order_view.xml',
        'views/pos_subscription_views.xml',
        'views/pos_config_views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'sd_pos_sale_subscription/static/src/js/Screens/PaymentScreen/PaymentScreenExt.js',
            'sd_pos_sale_subscription/static/src/js/Screens/ProductScreen/ProductScreenExt.js',
            'sd_pos_sale_subscription/static/src/js/models.js',
        ]
    },

}
