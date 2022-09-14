# -*- coding: utf-8 -*-
{
    'name': "Work Streams",

    'summary':
        """
            Work Stream and process.
            1: Work stream and process
            2: Link WS and Process with Tasks
            3: Lucid chart with Processes
        """,

    'description':
        """
            Work Stream and processes
            Task: T37139,
        """,

    "author": "Silverdale",
    "website": "https://www.silverdaletech.com",
    "category": 'Project',
    "version": '2207',

    'depends': ['base', 'project'],

    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/work_stream.xml',
        'views/work_stream_processes.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,

}
