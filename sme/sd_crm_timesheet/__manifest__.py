# -*- coding: utf-8 -*-
{
    'name': "CRM Timesheet",

    'summary': "Will record timesheets on lead",

    'description': """
        1: Allow user to record timesheets on lead
        2: Link analytic account to SO that is created on lead
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'CRM',

    'depends': ['base', 'sd_crm', 'hr_timesheet', 'hr', 'timer', 'analytic','sd_base_setup'],

    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/res_config_settings_views.xml',
        'wizard/crm_lead_create_timesheet_views.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,

}
