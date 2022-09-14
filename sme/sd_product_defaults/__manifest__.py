# -*- coding: utf-8 -*-

{
    "name": "SME Product Defaults",

    "summary": "barcode and reference auto generated on product creation",

    "description": """
        1: barcode and reference auto generated on product creation if rule is set in inventory settings
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": "Inventory",
    "depends": [
        'product', 'stock', 'sd_base_setup'
    ],
    "data": [
        "data/product_template_sequence.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
        "views/res_config_settings_views.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
