# -*- coding: utf-8 -*-
{
    "name": "SME Helpdesk CRM",
    "summary": "Create Opportunities from Helpdesk Ticket",

    "description": """
        1: Link Helpdesk with CRM.
        1: Create Opportunities from Helpdesk Ticket.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": "Helpdesk",

    "depends": [
        'sd_helpdesk', 'helpdesk', 'crm',
    ],
    "data": [
        "views/crm_lead_views.xml",
        "views/helpdesk_ticket_views.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
