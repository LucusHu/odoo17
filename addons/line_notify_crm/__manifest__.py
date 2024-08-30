{
    'name': 'Line Notify : CRM',
    'version': '1.1',
    'category': 'Services',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'OPL-1',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3','OPL-1',
    'summary': 'Line Notify CRM',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.建立【商機】後,將通知被指定業務經理
        2.發送內容固定
        "您有客戶報價需求：XXX(客戶報價)，已開立，請盡速處理\r\n"
        "連結：{web}
        3.建立【商機】後,將通知已被標記「商機」的聯絡人
        3.文本內容則在「商機」標籤內定義
    ''',
    # 'website': 'Your Website',
    'depends': [
        'line_notify',
        'crm',
    ],
    'data': [
        'data/notify_category_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
