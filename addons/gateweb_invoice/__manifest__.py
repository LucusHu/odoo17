{
    'name': 'GateWeb 第三方電子發票模組',
    'version': '1.7',
    'category': 'Accounting',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': '電子發票 (Invoice): GateWeb 關網第三方電子發票模組',
    'author': 'Lucas',
    'description': '''
    GateWeb API 界接
    §功能:
        1.開立發票,作廢發票,折讓發票
        2.產生A4/A5 PDF發票
    【版本v1.6】
        1.GateWeb參數設定移動至【一般設定】
        2.增加測試模式
    【版本v1.7】
        1.稅額修正:免稅,零稅率設定異常修補
        2.API中Description 修正從欄位name->product_id.name
    ''',
    # 'website': 'Your Website',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/paper.xml',
        'views/gateweb_invoice_trash_views.xml',
        'views/gateweb_invoice_allowance_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'report/invoice_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
