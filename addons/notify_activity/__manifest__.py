{
    'name': 'Mail活動系統',
    'version': '1.2',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Mail活動系統',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.發送郵件會將活動內容一併發送
    【版本v1.1】
        1.每日針對所有User的預期活動&過期活動,發送Line訊息提醒
    【版本v1.2】
        1.修正無法每日預期活動&過期活動,發送Line訊息提醒
    ''',
    'depends': [
        'mail',
        'notify',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/mail_activity_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
