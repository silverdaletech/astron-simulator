# -*- coding: utf-8 -*-
{
    "name": "SME Sales on CRM",
    "summary": "CRM: Add sales and CRM related functionlities",

    "description": """
       CRM: Add sales and CRM related functionlities
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": "CRM",

    "depends": [
        "base", "crm", "sale_management", 'sale_crm','sd_base_setup'
    ],

    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/res_config_settings_views.xml",
        "views/crm_price_role.xml",
        "views/crm_team_member_view.xml",
        "views/crm_lead_view.xml",
        "views/sale_order_view.xml",
        "report/crm_product_report_views.xml"
    ],

    "application": True,
    "installable": True,
    "auto_install": False,
}
