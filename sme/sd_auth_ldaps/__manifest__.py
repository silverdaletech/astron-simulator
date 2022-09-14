# -*- coding: utf-8 -*-
{
    'name': "SME LDAPS Authentication",
    'summary': "SME LDAPS Authentication",
    'description': """
        Patch to use LDAPS protocol instead of LDAP over TLS.
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    'category': 'Tools',

    "depends": [
        "auth_ldap"
    ],
    "data": [
    ],

    "application": False,
    "installable": True,
    "auto_install": False,
}
