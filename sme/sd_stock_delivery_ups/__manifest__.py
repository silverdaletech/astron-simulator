# -*- coding: utf-8 -*-
{
    "name": "SME UPS on Delivery order",
    'summary': " Add UPS on Delivery order",

    'description': """
        1: This module adds UPS on Delivery order.
           
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": 'Inventory',
    "depends": [
        "delivery", "sd_stock_delivery", "delivery_ups",
    ],
    "data": [
        "views/res_partner_view.xml",

    ],

    "application": False,
    "installable": True,
    "auto_install": False,
}
