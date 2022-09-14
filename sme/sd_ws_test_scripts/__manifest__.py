# -*- coding: utf-8 -*-
{
    "name": "Test Script Workstream",
    "description": """

        This module will link Test Scripts with Process and Work Stream.
         
        """,
    'summary': """
               This module will link Test Scripts with Process and Work Stream.
                1: Link Test Scripts to Processes
                2: Link Test Scripts to Work Stream.
               """,
    "version": "2207",
    "category": "Project",
    'author': "Silverdale",
    'company': "Silverdaletech",

    "depends": ["sd_ws", "sd_test_scripts", 'sale'],

    'data': [

        'security/ir.model.access.csv',
        'views/test_scripts_view.xml',
        'views/process.xml',
    ],

    'images': ['static/description/icon.png'],

    'demo': [
    ],
    'auto_install': False,
    "installable": True,
    'application': True,
}
