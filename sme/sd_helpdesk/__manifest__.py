# -*- coding: utf-8 -*-
{
    'name': "SME Helpdesk",

    'summary': "Enable Helpdesk features develop by Silverdale.",

    'description': """
        1: Helpdesk timesheet
        1: Create Opportunities from Ticket
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Helpdesk',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sd_base_setup', 'project','helpdesk_timesheet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/view_res_config_setting.xml',
        'views/view_ticket_rootcause.xml',
        'views/view_helpdesk_ticket.xml',
        'views/view_project_task.xml',
        'views/view_helpdesk_team.xml',
        'views/helpdesk_portal_templates.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

