{
    'name': 'BdCalling Billing Management',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Billing management with product category filtering',
    'description': """
        BdCalling Billing Management System
        Adds product category field to filter products in sale order lines.
    """,
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'depends': ['sale', 'product', 'account', 'sale_management', 'stock'],
    'data': [
        'views/sale_order_views.xml',
        'views/product_views.xml',
        'views/pricelist_views.xml',
        'views/sale_views.xml',
        'views/sale_order_report_views.xml',
        'views/account_move_views.xml',
        'report/sale_report_templates.xml',
        'report/sale_report_reports.xml',
         'report/report_with_test.xml',
        # 'views/report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}