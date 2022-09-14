{
    "name": "SME Project Timesheet",
    "summary": "Feature of Task Type and Billable checkbox on tasks.",

    "description": """
        Feature of Hide Timesheets from portal based on task type.
        Feature of Task billable/non-billable based on task type.
        Feature of Timesheet Manager and Approver related fields from employee to Timesheets.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": "Project",

    "depends": [
        "sd_project", "sd_timesheet", "hr_timesheet", "timesheet_grid", "sale_timesheet"
    ],

    "data": [
        "security/security.xml",
        "views/view_timesheet.xml",
        "views/project_view.xml",
        "views/res_config_setting.xml",
        "views/task_type.xml",
        "views/project_task.xml",
    ],

    "application": False,
    "installable": True,
    "auto_install": False,
}