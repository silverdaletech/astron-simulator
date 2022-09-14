{
    'name': "SME Product Brand Manager",

    'summary': "Product Brand Manager",
    
    'description': """
        1: This Module is use to set product brand on product
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': "Product",

    # any module necessary for this one to work correctly
    'depends': ["sale"],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        "views/product_brand_view.xml",
        "reports/sale_report_view.xml",
        "reports/account_invoice_report_view.xml",
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
