# -*- coding: utf-8 -*-
{
    'name': "SME Point of Sale Extension",
    
    'summary': "Customization related to point of sales",
    
    'description': """
        T8047, T8099, T8098(task removed), T17251
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Point of Sale',

    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_config_views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'sd_pos/static/src/css/popups/common.css',
            'sd_pos/static/src/js/Screens/ReceiptScreen/OrderReceiptExt.js',
            'sd_pos/static/src/js/Popups/ClosePosPopupExt.js',
            'sd_pos/static/src/js/Screens/ProductScreen/ProductScreenExt.js',
            'sd_pos/static/src/js/Popups/EditListPopupExt.js',
            'sd_pos/static/src/js/Popups/LotLine.js'
        ],
        'web.assets_qweb': [
            'sd_pos/static/src/xml/Screens/ReceiptScreen/OrderReceiptExt.xml',
            'sd_pos/static/src/xml/Popups/ClosePosPopupExt.xml',
            'sd_pos/static/src/xml/Popups/EditListPopupExt.xml',
            'sd_pos/static/src/xml/Popups/LotLine.xml'
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
