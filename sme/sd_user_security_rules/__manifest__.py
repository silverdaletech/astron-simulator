# -*- coding: utf-8 -*-
{
    'name': "SME User Security Roles",

    'summary': "The tool to combine users in roles and to simplify security group assigning",

    'description': """
       The tool to combine users in roles and to simplify security group assigning
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['sd_base_setup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/security_role.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
