{
    "name": "Password Security",
    "summary": "Allow admin to set password security requirements.",
    'description': """
        Allow admin to set password security requirements on company level it contain following features
        1: Password expiration days
        2: Password length requirement
        3: Password minimum number of lowercase letters
        4: Password minimum number of uppercase letters
        5: Password minimum number of numbers
        6: Password minimum number of special characters
        7: Password strength estimation
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": "Base",

    "depends": [
        "auth_signup",
        "auth_password_policy_signup","sd_base_setup"
    ],

    "external_dependencies": {
        "python": ["zxcvbn"],
    },

    "data": [
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "security/res_users_pass_history.xml",
    ],

    'assets': {
        'web.assets_common': [
            'sd_password_security/static/src/js/password_gauge.js',
            'sd_password_security/static/lib/zxcvbn/zxcvbn.min.js',
        ],
    },

    "demo": [
        "demo/res_users.xml",
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
