# -*- coding: utf-8 -*-
{
    'name': "SME User Restriction",
    'summary': "Access Restriction for Users",

    'description': """
        This will help in Login Restriction for user base on IPs and Mac Address.
    """,

    'author': 'Silverdale',
    'website': 'https://www.silverdaletech.com',
    "category": 'Manufacturing',
    "version": '2208',

    'depends': ['base', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        'views/view_user.xml',
        'views/view_res_config_setting.xml',
    ],
}
