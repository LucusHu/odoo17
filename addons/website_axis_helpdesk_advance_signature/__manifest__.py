{
    'name': 'Advance Helpdesk, Signature',
    'version': '2.2',
    'category': 'Services/Helpdesk',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'OPL-1',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': 'Signature',
    'author': 'Lucas',
    'description': '''
    §功能:
        1.發送連結讓客戶簽名
    ''',
    # 'website': 'Your Website',
    'depends': [
        'website_axis_helpdesk_advance',
    ],
    'data': [
        'views/axis_helpdesk_ticket_views.xml',
        'views/axis_helpdesk_ticket_signature_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_axis_helpdesk_advance_signature/static/src/signature_form/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
