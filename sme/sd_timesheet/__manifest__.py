{
    "name": "SME Sale Timesheet",
    "summary": "Feature of non-billable timesheets on ticket.",
    "description": """
        Add all the fields to timesheet related to billable/ non-billable.
    """,
    'author': "Silverdale",
    'website': "https://wwww.silverdaletech.com",
    'version': "2208",
    'category': "Timesheet",
    "license": "Other proprietary",

    "depends": [
         "timesheet_grid", "helpdesk_timesheet", "sale_timesheet",
    ],

    "data": [
        # "security/security.xml",
    ],

    "application": False,
    "installable": True,
    "auto_install": False,
}