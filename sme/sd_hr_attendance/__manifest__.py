# -*- coding: utf-8 -*-
{
    'name': "SME Attendance",

    'summary': "Enable Attendance features develop by Silverdale.",

    'description': """
        1: Attendance on Portal
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Human Resources/Attendances',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'sd_base_setup', 'hr_attendance'],

    # always loaded
    'data': [
        'views/view_res_config_setting.xml',
        'views/portal_attendance_template.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

