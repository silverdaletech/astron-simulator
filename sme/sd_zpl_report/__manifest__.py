# -*- coding: utf-8 -*-
{
    'name': "SME ZPL Label Designer",
    'summary': "ZPL Label Designer",
    'description': """
        This App Will let you create Custom ZPL Labels.
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2206',
    'category': 'ZPL Reports',
    'depends': ['base', 'mail', 'sd_widgets', 'sd_base_setup', ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/zpl_design_preview_view.xml',
        'wizard/zpl_custom_content_view.xml',
        'views/template.xml',
        'views/zpl_label_size_view.xml',
        'views/zpl_label_design_view.xml',
        'views/menu.xml',
    ],
    'external_dependencies': {
        'python': ['zpl'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
