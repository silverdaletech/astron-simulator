# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "SME Sale Agreements",
    'summary': "Silverdale Module Extension for Sale Agreement.",

    'description': """
        Functionality to manage your Sale Agreements.
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    "license": "OPL-1",
    'version': '2209',
    'category': 'Sale',

    'depends': ['sale', 'portal','stock','sale_management','sd_base_setup'],
    'data': [
        'security/sale_agreement_security.xml',
        'security/ir.model.access.csv',
        'data/sale_agreement_data.xml',
        'views/view_res_config_setting.xml',
        'views/templates.xml',
        'views/sale_views.xml',
        'views/sale_agreement_views.xml',
        'wizard/sale_agreement_wizard.xml',

        'report/report_sale_agreement.xml',
        'report/reports.xml',
        'report/mail_template_data.xml',
       
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
