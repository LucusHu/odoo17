{
    'name': 'Notify : Account',
    'version': '1.0',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Notify Account ',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.按下「發送與列印」將通知已被標記「會計」的聯絡人
        2.文本內容則在「會計」標籤內定義
    ''',
    # 'website': 'Your Website',
    'depends': ['notify', 'account', ],
    'data': ['data/notify_category_data.xml', ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
