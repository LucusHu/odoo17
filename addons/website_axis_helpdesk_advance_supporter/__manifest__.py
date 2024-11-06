{
    'name': 'Advance Helpdesk, Supporter',
    'version': '2.5',
    'category': 'Services/Helpdesk',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'OPL-1',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': 'Supporter, Process hours, Auto Engineer',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.支援工程師
        2.處理時數
        3.設備編號(必填)   
    【版本v2.4】 
        1.設備編號(必填)  
    【版本v2.5】
        1.團隊欄位->(必填)
    ''',
    # 'website': 'Your Website',
    'depends': [
        'website_axis_helpdesk_advance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/axis_helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
