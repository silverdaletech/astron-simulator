# -*- coding: utf-8 -*-
{
    'name': "SME Website Maintenance Mode",
    'summary': "Maintenance Mode on website",

    'description': """
       1: This module will set maintenance Mode on website if database upgrade is in process!!!
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'website',

    # any module necessary for this one to work correctly
    'depends': ["base", "web", 'sd_base_setup', 'website'],

    # always loaded
    'data': [
        "views/template_maintenence_mode.xml",
        "views/view_res_config_setting.xml"
    ],

    "application": True,
    "installable": True,
    "auto_install": False,
}
