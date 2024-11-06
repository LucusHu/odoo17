{
    'name': '銷售-NH',
    'version': '1.0',
    'category': 'Sales',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3','OPL-1',
    'summary': '',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.查詢添加手機號碼
    ''',
    # 'website': 'Your Website',
    'depends': ['sale', ],
    'data': [
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
