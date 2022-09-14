# -*- coding: utf-8 -*-
{
    'name': "SME Equipment to Asset",

    'summary': "Connection between assets in accounting to the Equipment made in maintenance app",

    'description': """
      Connection between assets in accounting to the Equipment made in maintenance app
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Sale',

    # any module necessary for this one to work correctly
    'depends': [
        "base", "maintenance", "purchase", "stock", "sale", "account_asset"
    ],

    'data': [
        "security/security.xml",
        "views/res_config_settings_views.xml",
        "views/product_template_view.xml",
        "views/stock_picking_view.xml",
        "views/account_move_view.xml",
        "views/maintenance_view.xml",
        "views/purchase_view.xml",
        "views/account_asset_view.xml",
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
