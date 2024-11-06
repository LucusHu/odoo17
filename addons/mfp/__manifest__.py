{
    'name': 'MFP 雲端抄表系統',
    'category': 'Services',
    'version': '2.4',
    'summary': 'MFP 雲端抄表系統',
    'description': '''
    §功能:
        1.事務機抄表系統
    【版本v2.3】
        1.新增【待機區】
        2.【帳單計算】,將預收與扣抵顯示移除
        3.修正發送異常問題
    【版本v2.4】
        1.修正自動做帳單 & 手動作帳單
    ''',
    'depends': ['base', 'account', ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/place_data.xml',
        'data/brand_data.xml',
        'data/model_ricoh_data.xml',
        'data/model_xerox_data.xml',
        'data/model_toshiba_data.xml',
        'data/product_data.xml',
        'data/record_data.xml',
        'data/tooltip_data.xml',
        'data/ir_cron.xml',
        'report/account_move_report.xml',
        'views/report_invoice.xml',
        'views/account_move_views.xml',
        'views/brand_views.xml',
        'views/contract_views.xml',
        'views/install_record_views.xml',
        'views/invalid_record_views.xml',
        'views/mfp_data_views.xml',
        'views/mfp_record_views.xml',
        # 'views/mfp_record_category_views.xml',
        'views/res_partner_views.xml',
        'views/place_views.xml',
        'wizard/mfp_calc_manual_wizard.xml',
        # 'wizard/mfp_calc_manual_exchange_wizard.xml',
        # 'wizard/account_move_exchange_calc.xml',
        'views/menu.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
