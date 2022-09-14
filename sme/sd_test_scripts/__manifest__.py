# -*- coding: utf-8 -*-
{
    "name": "Test Scripts",
    "description": """

        This module will allow adding test scripts functionality into the system.
         Task : T37139,
        """,
    'summary': """
               This module will allow adding test scripts functionality into the system.
                1: Test Scripts
                2: Link Test Scripts to Tasks
                3: Link Test Scripts to Tickets
                4: Link Test Scripts to Access Levels
                5: Link Test Scripts to Projects based on tasks test scripts.
               """,
    "version": "2206",
    "category": "Project",
    'author': "Silverdale",
    'company': "Silverdale",

    "depends": ["project", "helpdesk"],

    'data': [

        'security/ir.model.access.csv',
        'views/test_scripts_view.xml',
        'views/project_view.xml',
        'views/task_view.xml',
        'views/ticket_view.xml',


    ],

    'images': ['static/description/icon.png'],

    'demo': [
    ],
    'auto_install': False,
    "installable": True,
    'application': True,
}
