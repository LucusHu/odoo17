{
    "name": "Notify系統",
    "version": "2.3",
    "category": "Services",
    "license": "LGPL-3",
    "summary": "Notify User/Partner",
    "author": "Lucas",
    'description': '''
    §功能:
        1.介接Line API 發送Line訊息
        2.僅對使用者&客戶的聯絡人發送
    【版本v2.3】
        1.增加聯絡人欄位【通知】
        2.文本內容則在「會計」標籤內定義
    ''',
    # "website": "Your Website",
    "depends": [
        "base",
        "contacts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/res_users_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/notify_category.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
