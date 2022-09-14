# -*- coding: utf-8 -*-
{
    'name': "SME Website First & Last name",

    'summary': "Website First & Last name",

    'description': """
        Website First & Last name
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Website',

    # any module necessary for this one to work correctly
    "depends": [
        'sd_partner_firstname',
        'website_sale',
    ],
    # always loaded
    "data": [
        'views/website.xml',
    ],
    'application': True,
    "installable": True,
    "auto_install": False,
}
