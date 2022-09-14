{

    "name": "SME Project",

    "summary": "This module will add features in Project Module",
    "description": """
        This module will add features in Project Module
        Functionality of Adding Milestone Menu in Project.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    "category": "Project",

    "depends": [
        "base", "project", "sd_base_setup"
    ],

    "data": [
    # 'security/view_res_group.xml',
        'security/ir.model.access.csv',
        "views/task_type.xml",
        "views/project_task.xml",
        "views/res_config_setting.xml",
        "views/view_project.xml",
        "views/project_portal.xml",
        "views/project_stages.xml",
        "views/task_stages_view.xml",
        "views/project_milestone.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sd_project/static/src/js/project_form.js',
        ]
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}
