{
    'name': ' BdCalling LC Management',
    'version': '1.0',
    'summary': 'Letter of Credit Management for Purchase Orders',
    'description': """
        Automatically create Letter of Credit records from confirmed Purchase Orders.
        ===========================================================================
        
        Features:
        - Creates LC record automatically when Purchase Order is confirmed
        - Copies all PO lines to LC lines
        - Tracks LC reference on Purchase Order
        - Simple LC management interface
    """,
    'category': 'bd_calling',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    
    'depends': ['base', 'mail','purchase'],
    
    'data': [
        'security/ir.model.access.csv',
        'data/lc_sequence.xml',
        'views/purchase_views.xml',
        'views/lc_views.xml',
        'views/payment_terms_views.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    
    
    
   
}