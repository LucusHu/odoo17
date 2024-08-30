{
    'name': 'Line Notify : Project',
    'version': '1.0',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Line Notify Project ',
    'author': 'Lucas',
    'description': '''
     §功能:
        1.建立【客服單】後通知被指定的負責人員
        發送內容固定:
        "專案【XXX】已新增\r\n
        連結：{web}"
        2.變更[狀態]後,將通知被指定的負責人員
        發送內容固定:
        專案【XXX】狀態已變更為【觀察中】
        連結：{web}"
    ''',
    # 'website': 'Your Website',
    'depends': [
        'base',
        'contacts',
        'line_notify',
        'project',
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
