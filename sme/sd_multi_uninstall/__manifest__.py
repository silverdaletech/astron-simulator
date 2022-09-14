# -*- coding: utf-8 -*-
{
    'name': "SME Modules Uninstall",
    
    'summary': "Bulk Modules uninstall.",
    
    'description': """
        This module help you to select multiple modules and all selected modules can be uninstalled on a single click.
        Select the modules to un-installed from the tree view and click on the action un-installed!!!
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Base',

    'depends': ["base", "web"],

    'data': [
        "views/view_multiple_module_uninstall.xml"
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
