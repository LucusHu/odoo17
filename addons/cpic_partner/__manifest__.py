{
    'name': 'CPIC 客製化系統',
    'version': '1.0',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Customer system of CPIC',
    'author': 'Lucas',
    'description': '''
        §功能(創勁專用):
        1.客製化系統
    ''',
    # 'website': 'Your Website',
    'depends': ['base', 'contacts', 'crm', 'product', ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
