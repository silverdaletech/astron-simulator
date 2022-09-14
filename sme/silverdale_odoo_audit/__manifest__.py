# -*- coding: utf-8 -*-
{
    'name': "SME Odoo Audit",

    'summary': "Silverdale Odoo Audit Application",

    'description': """
        1: Silverdale Odoo Audit Application. 
        2: It audits the custom code 
        3: and the configuration you did on your odoo instance.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Sale',

    # any module necessary for this one to work correctly
    'depends': ['sd_base_setup', 'portal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/seq.xml',
        'data/ir_config.xml',
        'views/menus.xml',

        'views/odoo_audit_view.xml',
        'views/res_config_view.xml',
        'views/industry_type_view.xml',
        'views/audit_addons_list.xml',
        'views/master_data_view.xml',
        'views/duplicated_data_view.xml',

        'reports/report_layout.xml',
        'reports/audit_report.xml',
        'reports/report.xml',

        'wizard/audit_addons_lsit_view.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False
}
