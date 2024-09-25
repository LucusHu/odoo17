{
    'name': '會計模組(Printer)',
    'version': '1.0',
    'category': 'Accounting',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': '會計模組(Printer)',
    'author': 'Lucas',
    'description': '''
    會計模組
    §功能:
        1.增添欄位subject_remark
    ''',
    # 'website': 'Your Website',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
