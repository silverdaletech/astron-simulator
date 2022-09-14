# -*- coding: utf-8 -*-
{
    'name': 'SME Vimeo Videos - eLearning Platform',
    'summary': "Manage vimeo videos in elearning platform",
    'description': """ 
        1: The vimeo video links will render same as youtube video links in E-Learning module 
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    "category": 'Website',

    'depends': ['website_slides','sd_base_setup'],
    'data': [
        'views/slide_slide.xml',
        'views/template_lesson.xml',
        ],

    'assets': {
        'web.assets_common': [
            'sd_vimeo_video/static/src/css/styles.scss'
        ],
        'web.assets_frontend': [
            'https://player.vimeo.com/api/player.js',
            'sd_vimeo_video/static/src/js/main_script.js',
        ],
    },

    'installable': True,
    'auto_install': True,
    'application': True,
}
