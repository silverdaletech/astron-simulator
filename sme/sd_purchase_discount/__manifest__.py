# -*- coding: utf-8 -*-
{
    'name': "SME Purchase Discounts",
    
    'summary': "This will Allow Feature of Discounts on Purchase order line develop by Silverdale.",

    'description': """
        This will Allow Feature of  Discounts on Purchase order line develop by Silverdale.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Purchase Management',

    # any module necessary for this one to work correctly
    "depends": ["purchase_stock"],

    # always loaded
    "data": [
        "views/purchase_discount_view.xml",
        "views/report_purchaseorder.xml",
        "views/product_supplierinfo_view.xml",
        "views/res_partner_view.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
