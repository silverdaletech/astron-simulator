# -*- coding: utf-8 -*-
{
    'name': "Task Logs",
    'summary': """

        Will create different logs of Task""",

    'description': """
        This module will create Task stages logs and planned hours logs.
    """,

    'author': "Silverdale",
    'website': "http://www.silverdaletech.com",
    'category': 'Project',
    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/task_hours_logs_view.xml',
        'views/project_task_view.xml',
        'views/task_stages_logs_view.xml',
    ],
    
}
