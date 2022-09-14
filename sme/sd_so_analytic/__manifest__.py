{
    'name': "SME Default Sale Order Analytic Account ",
    
    'summary': "This will add default analytic account on sale order and sale order line.",
    
    'description': """
        This will add default analytic account on sale order and sale order line.and set analytic account on invoice 
        lines from sale order line
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2207',
    'category': 'Accounting',
    'depends': ['account', 'sale', 'analytic', 'sd_sale', 'sd_base_setup'],
    
    'data': [
            'views/sale_order_view.xml',
            'views/analytic_account_inherit.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False
}
