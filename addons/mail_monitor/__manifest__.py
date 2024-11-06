{
    "name": "Mail郵件系統",
    "version": "1.1",
    "category": "Services",
    # "Accounting", # "Sales", # "Services"
    "license": "LGPL-3",
    # "MIT", "BSD", "Apache", "LGPL-3", "GPL-3", "AGPL-3",
    "summary": "Mail郵件系統",
    "author": "Lucas",
    'description': '''
     §功能:
        1.監測Mail Server信件
        2.設定【關鍵字】,並對特定格式去解析
        3.針對符合【關鍵字】的郵件,開立客服單
    【版本v1.1】
        1.修正無法開立客服單問題  
    ''',
    # "website": "Your Website",
    "depends": ["mail", "cpic_partner", ],
    "data": [
        "security/ir.model.access.csv",
        "views/server_mail_views.xml",
        "views/filter_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
