# __manifest__.py
{
    'name': 'BD Calling Requisition',
    'version': '19.0.1.0.0',
    'category': 'Operations/Approvals',
    'summary': 'Add BD Calling product lines to Approval requests',
    'depends': ['approvals', 'product','base', 'stock','purchase'],
    'data': [
        
        'views/approval_inherit_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}