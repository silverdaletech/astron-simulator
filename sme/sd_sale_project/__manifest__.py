# -*- coding: utf-8 -*-
{
    'name': "SME Sale Project",

    'summary': "Project Requirement on SO Level ",

    'description': """
        1: Will add new field on SO line for project description and when project created from line 
        it will populate description in project description
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'sale',

    'depends': ['base', 'sd_sale', 'sale_project', 'sd_base_setup'],

    'data': [
        'views/sale_order.xml',
    ],
}
