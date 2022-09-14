# -*- coding: utf-8 -*-
{
    "name": "SME USPS on Delivery order",
    'summary': " Add USPS on Delivery order",

    'description': """
            1: This module adds USPS on Delivery order.

        """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": 'Inventory',
    "depends": [
        "sd_stock_delivery", "delivery_usps"
    ],
    "data": [
        "views/res_partner_view.xml",
    ],

    "application": False,
    "installable": True,
    "auto_install": False,
}
