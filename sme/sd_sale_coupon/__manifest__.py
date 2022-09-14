# -*- coding: utf-8 -*-
{
    'name': "SME Sale Coupon",

    'summary': "Promotion stack",

    'description': """
        When multiple discounts are applied, only carry out ONE and the MOST DESIREABLE one.
        Will apply only program that is highest min qty meet.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'sales',

    'depends': ['base', 'sale_coupon'],

    'data': [
        'views/sale_order_views.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}