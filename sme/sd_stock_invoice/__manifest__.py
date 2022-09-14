# -*- coding: utf-8 -*-
{
    'name': "Create Invoice from Stock",
    'summary': "Automatic Invoice on delivery confirmation",
    'description': """
        Automatic Invoice on delivery confirmation
    """,

    'author': "Silverdale",
    'website': "https://wwww.silverdaletech.com",
    'license': 'Other proprietary',
    'version': '2206',
    'category': "Accounting",
    'depends': ["base", "stock", "account", 'mail', 'sale', 'sd_stock'],
    'data': [
        "views/view_res_config_setting.xml",
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
