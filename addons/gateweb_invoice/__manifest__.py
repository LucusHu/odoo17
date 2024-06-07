# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'GateWeb 第三方電子發票模組',
    'version': '1.5',
    'category': 'Accounting',
    # 'Accounting', # 'Sales', # 'Services'
    'license': 'LGPL-3',
    # 'MIT', 'BSD', 'Apache', 'LGPL-3', 'GPL-3', 'AGPL-3',
    'summary': '電子發票 (Invoice): GateWeb 關網第三方電子發票模組',
    'author': 'Lucas',
    'description': '電子發票 (Invoice): GateWeb 關網第三方電子發票模組',
    # 'website': 'Your Website',
    'depends': [
        'base',
        # 'contacts',
        'account',
        # 'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/account_move_views.xml',
        # 'views/test_views.xml',
        # 'report/account_move_report.xml',
        # 'wizard/account_move_calc.xml',
        # 'views/menu.xml',
        # 'data/sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
