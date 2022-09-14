# -*- coding: utf-8 -*-
{
    'name': "SME Stock Report",
    'summary': "Add QR code instead of Barcode on transfer print report",
    'description': """
        This module will add following 
        1 : QR code instead of Barcode on transfer print report
    """,

    'author': "Silverdale",
    'website': "https://wwww.silverdaletech.com",
    'license': 'Other proprietary',
    'version': '2206',
    'category': "Inventory",
    'depends': [
        "base", "stock","sd_base_setup"
    ],
    'data': [
        'report/stock_picking_report_ext.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}