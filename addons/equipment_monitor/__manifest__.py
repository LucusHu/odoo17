# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Equipment Monitor",
    "version": "1.0",
    "category": "Services",
    "license": "LGPL-3",
    "summary": "Manage information of equipment monitor.",
    "author": "Lucas",
    'description': '''
    §功能(創勁專用):
        1.小幫手
    ''',
    # "website": "Your Website",
    "depends": [
        "base",
        "contacts",
        # "account",
        # "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        # "views/account_data_views.xml",
        "views/hardware_type_views.xml",
        "views/hardware_views.xml",
        "views/software_views.xml",
        "views/nic_views.xml",
        "views/monitor_views.xml",
        "views/monitor_parameter_views.xml",
        "views/smart_views.xml",
        "views/smart_line_views.xml",
        "views/eqpt_views.xml",
        "views/res_partner_views.xml",
        # "report/account_move_report.xml",
        # "wizard/account_move_calc.xml",
        "views/menu.xml",
        # "data/sequence.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
