{
    'name': "SME Address Validation",
    'summary': "Silverdale App for USPS address validation for partner addresses",
    'description': """
        Silverdale App for USPS address validation for partner addresses
    """,
    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',

    'depends': ['contacts', 'sd_sale', 'stock', 'website_sale', 'sd_contact'],

    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/sale_order_view.xml',
        'views/view_res_config_setting.xml',
        'views/stock_picking_view.xml',
        'views/template.xml',
        'views/address_validate_template.xml',
        'wizard/address_validate_selector_wizard.xml',
    ],

    'external_dependencies': {
        'python': ['pyusps']
    },

    'installable': True,
    'application': False,
}
