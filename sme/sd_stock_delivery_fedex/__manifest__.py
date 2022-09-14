{
    'name': "SME Fedex on Delivery order",

    'summary': " Add Fedex on Delivery order",

    'description': """
        1: This module adds Fedex on Delivery order.
           
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": 'Inventory',

    # any module necessary for this one to work correctly
    'depends': ["base","sd_stock_delivery", "delivery_fedex"],

    # always loaded
    'data': [
        "views/res_partner_view.xml",
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
