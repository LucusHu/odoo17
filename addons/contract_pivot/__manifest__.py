{
    "name": "Recurring - Contracts Management Pivot",
    'version': '1.0',
    "category": "Contract Management",
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'AGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3','OPL-1',
    'summary': 'Recurring - Contracts Management',
    'author': 'Lucas',
    'description': '''
    ''',
    # 'website': 'Your Website',
    'depends': ['contract', ],
    'data': [
        # 'data/ir_cron.xml',
        # 'data/mail_activity_data.xml',
        'security/ir.model.access.csv',
        'views/contract_tag_category.xml',
        'views/contract.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
