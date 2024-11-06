{
    'name': '薪資系統',
    'version': '1.1',
    'category': 'Services',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3','OPL-1',
    'summary': '薪資系統',
    'author': 'Lucas',
    'description': '''
    §功能(創勁專用):
        1.【合約】增加勞工保險
        2.【合約】增加全民健康保險
    【版本v1.1】
        1.【合約】增加
    ''',
    # 'website': 'Your Website',
    'depends': [
        'base',
        # 'contacts',
        'om_hr_payroll',
        # 'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_extra_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
