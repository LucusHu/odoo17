{
    "name": "Mail郵件系統",
    "version": "1.0",
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
        2.針對符合【關鍵字】的郵件,開立客服單
    ''',
    # "website": "Your Website",
    "depends": [
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        # "views/account_data_views.xml",
        "views/server_mail_views.xml",
        "views/filter_views.xml",
        # "report/account_move_report.xml",
        # "wizard/account_move_calc.xml",
        "views/menu.xml",
        # "data/sequence.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
