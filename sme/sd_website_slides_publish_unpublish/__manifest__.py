# -*- coding: utf-8 -*-
{
    "name": "SME eLearning Publish/UnPublish",
    'summary': "This will add Publish/UnPublish features in eLearning developed by Silverdale.",

    'description': """
        1: This will add Publish/UnPublish features in eLearning module developed by Silverdale..
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'eLearning',

    "depends": ["website_slides",'sd_base_setup'],

    "data": [
        "views/slide_channel_view.xml",
        "views/slide_content_view.xml",
    ],

    "application": True,
    "installable": True,
    "auto_install": False,

}
