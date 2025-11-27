{
    'name': 'BdCalling Sales Management',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Sales Management Portal for Sales Team Members',
    'description': """
        Sales Management Portal for sales team members to manage contacts and sales activities.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'web',
        'portal',
        'website',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_user_views.xml',
        'views/res_partner_views.xml',
        'views/contact_portal.xml',
        'views/todo_portal.xml',
        'views/quotation_portal.xml',
        'views/dashboard_main.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
