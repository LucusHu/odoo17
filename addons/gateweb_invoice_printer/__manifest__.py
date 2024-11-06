{
    'name': 'GateWeb 第三方電子發票模組(Printer)',
    'version': '1.0',
    'category': 'Accounting',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': '電子發票 (Invoice): GateWeb 關網第三方電子發票模組(Printer)',
    'author': 'Lucas',
    'description': '''
    GateWeb API 界接
    §功能:
        1.於聯絡人增添欄位
        2.開立發票時,將採用此欄位參數取代buyer
    ''',
    # 'website': 'Your Website',
    'depends': ['gateweb_invoice', ],
    'data': ['views/res_partner_views.xml', ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
