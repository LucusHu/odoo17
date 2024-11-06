{
    'name': 'Equipment Maintenance',
    'version': '1.2',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Manage information of equipment maintenance.',
    'author': 'Lucas',
    'description': '''
    §功能(創勁專用):
        1.資訊設備:紀錄客戶設備類型&遠端連線
        2.帳號密碼:紀錄客戶帳號&密碼
        3.網路-軟體-密碼:紀錄客戶擁有的套裝軟體&帳密
    【版本v1.2】
        1.調整description Html,Char->Text
    ''',
    # 'website': 'Your Website',
    'depends': ['base_setup', 'mail', ],
    'data': [
        'security/ir.model.access.csv',
        'views/equipment_device_type_views.xml',
        'views/equipment_remote_type_views.xml',
        'views/equipment_views.xml',
        'views/account_connect_type_views.xml',
        'views/account_info_views.xml',
        'views/software_type_views.xml',
        'views/software_internet_type_views.xml',
        'views/software_views.xml',
        'views/res_partner_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
