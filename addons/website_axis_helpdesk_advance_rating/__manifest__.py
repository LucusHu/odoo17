{
    'name': 'Advance Helpdesk, Rating',
    'version': '2.0',
    'category': 'Services/Helpdesk',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'OPL-1',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': 'Rating',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.讓客戶評分
    ''',
    # 'website': 'Your Website',
    'depends': [
        'website_axis_helpdesk_advance',
    ],
    'data': [
        'views/axis_helpdesk_ticket_rating_templates.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'website_axis_helpdesk_advance_signature/static/src/signature_form/**/*',
    #     ],
    # },
    'installable': True,
    'application': False,
    'auto_install': False,
}
