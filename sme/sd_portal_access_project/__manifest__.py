# -*- coding: utf-8 -*-
{
    'name': "SME Portal Access: Project App",

    'summary': "Portal Access: Enable of Disable user to access Project  on Portal",

    'description': """
        Portal Access: Enable of Disable user to access Project on Portal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    'category': 'Sales',

    # any module necessary for this one to work correctly
    'depends': ['base','sd_contact', 'sd_project','sd_project_timesheet'],

    # always loaded
    'data': [

        'views/views.xml',
        'views/templates.xml',
        'views/project_templates.xml',
        'views/task_templates.xml',
        'views/task_view.xml',
        'views/project_view.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',

}
