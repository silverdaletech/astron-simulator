# -*- coding: utf-8 -*-
{
    'name': "SME Invite Multiple Attendees to join Multiple Courses",
    'summary': "Invite Multiple Attendees to join Multiple Courses",

    'description': """
        [T3384]
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'eLearning.',

    # any module necessary for this one to work correctly
    'depends': ['base','website_slides'],
    
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/invite_multiple_attendees_wizard.xml',
        'data/mail_template_data.xml',
        'views/menu.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
