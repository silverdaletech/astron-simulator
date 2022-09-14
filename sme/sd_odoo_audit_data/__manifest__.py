# -*- coding: utf-8 -*-
{
    "name": "SME Audit Master And Duplicate Data",

    "summary": "Master and Duplicate data for silverdale odoo audit module.",

    "description": """
        Master and Duplicate data for silverdale odoo audit module.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": "Base",

    "depends": [
        "base", "silverdale_odoo_audit",'sd_base_setup'
    ],
    "data": [
        "security/ir.model.access.csv",
    ],

    "application": False,
    "installable": True,
    "auto_install": False,
    'post_init_hook': 'post_init_hook',
}
