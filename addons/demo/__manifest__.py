{
    'name': '測試系統',
    'version': '1.0',
    'category': 'Services',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3','OPL-1',
    'summary': '',
    'author': 'Lucas',
    'description': '''
    ''',
    # 'website': 'Your Website',
    'depends': ['base', ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/demo_views.xml',
        # 'report/demo.xml',
        # 'wizard/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
