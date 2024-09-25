{
    'name': 'Stock: AVB',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3','OPL-1',
    'summary': 'Stock: AVB',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.新增庫存報表進貨單,出貨單,退貨單
    【版本v1.1】
    ''',
    # 'website': 'Your Website',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'data/paper.xml',
        'report/stock_picking_report_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        # 'views/stock_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
