# -*- coding: utf-8 -*-
{
    'name': "SME Event",

    'summary': "Hold attendee status un-confirm until payment",

    'description': """
        1: This will hold attendee status 'un-confirm' until payment status is not paid if auto confirmation is
            enable in event and ticket is paid
        2: This will remove registration section if no ticket attached in event
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'event',

    'depends': ['base', 'event_sale', 'sd_base_setup','website_event'],

    'data': [
        'views/event_view.xml',
        'views/event_registration_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
