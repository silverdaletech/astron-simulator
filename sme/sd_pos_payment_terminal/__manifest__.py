# -*- coding: utf-8 -*-
{
    "name": "SME: POS Payment Terminal Base",
    "summary": """
            This is base module to add  Payment terminal module  in POS. 
   """,
    "description": """
                1: Add stripe terminal
                2: Add Square Terminal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com/",

    'category': 'base',
    'version': '2208',
    'license': 'OPL-1',

    "depends": [
        "base", "point_of_sale",
    ],

    "data": [
        "views/res_config_settings_views.xml",
    ],

    "application": True,
    "installable": True,
    "auto_install": True,
}


