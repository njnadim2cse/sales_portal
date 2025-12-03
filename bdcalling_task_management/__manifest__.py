{
    'name': 'BDCalling Task Management',
    'version': '1.0',
    'category': 'Productivity',
    'summary': 'Simple task management module',
    'author': 'Your Name',
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_purpose_views.xml',
        'views/task_views.xml',  
        'views/menu.xml',        
    ],
    'images': [
        'static/description/icon.jpeg'
        ], 
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
