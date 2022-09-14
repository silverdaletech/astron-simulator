# -*- coding: utf-8 -*-
{
    'name': "SME Authoriz.net",
    'summary': "Silverdale Authorize.net",
    'description': """
        1: Use Invoice Address for billing details instead of Customer address.
        2: Use Company Name for billing if billing address doesn't have name setup. 
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    "license": "Other proprietary",
    'version': '2207',
    'category': 'Payment',
    'depends': ['payment', 'payment_authorize'],

    'data': [
        'views/payment_acquirer.xml'
    ],

    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}