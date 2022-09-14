{
    'name': "SME Shipping on Delivery order",

    'summary': "Add shippinng option on stock.",

    'description': """
        1: This module adds Shipping on delivery order.
            Remove delivery option from sale order.

    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Inventory',

    # any module necessary for this one to work correctly
    'depends': ["base", "stock", "delivery", "delivery_ups", "delivery_usps","sd_stock"],

    # always loaded
    'data': [
        "views/stock_picking_view.xml",
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
        "views/view_res_config_setting.xml",
        "wizard/picking_delivery_carrier_views.xml",
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
