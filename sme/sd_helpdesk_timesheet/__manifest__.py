{

    "name": "SME Helpdesk Timesheet",
    "summary": "Feature of non-billable timesheets on ticket.",

    "description": """
        Feature of non-billable timesheets on ticket.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": "Helpdesk",

    "depends": [
        'helpdesk_timesheet', 'sd_base_setup', 'sd_helpdesk','sd_timesheet',
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/helpdesk_ticket.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
