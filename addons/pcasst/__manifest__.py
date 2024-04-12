# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '小幫手系統',
    'category': 'Services',
    'version': '17.1',
    'summary': '小幫手系統',
    'description': "小幫手系統",
    'depends': [
        'base',
        'contacts',
        # 'account',
        # 'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'views/account_data_views.xml',
        'views/test_views.xml',
        'views/res_partner_views.xml',
        # 'report/account_move_report.xml',
        # 'wizard/account_move_calc.xml',
        'views/menu.xml',
        # 'data/sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
