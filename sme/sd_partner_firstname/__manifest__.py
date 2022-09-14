
{
    'name': "SME Partner first name and last name",
    
    'summary': "Split name into first and last name",
    
    'description': """
        1:This Module is use to split name into first and last name for non company partners.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Contacts',

    # any module necessary for this one to work correctly
    'depends': ["base_setup"],

    'data': [
        "views/base_config_view.xml",
        "views/res_partner.xml",
        "views/res_user.xml",
    ],
    'post_init_hook': "post_init_hook",
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
