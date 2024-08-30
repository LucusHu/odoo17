{
    'name': 'EZPay 第三方電子發票模組',
    'version': '1.5',
    'category': 'Accounting',
    'summary': '電子發票 (Invoice): EZPay 綠界第三方電子發票模組',
    'depends': ['account', 'sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting_view.xml',
        'views/account_invoice_view.xml',
        'views/ezpay_invoice_uniform_view.xml',
        # 'views/website_sale.xml',
        # 'views/sale_order_view.xml',
        'views/menu.xml',
        # 'data/demo.xml',
        'report/uniform_invoice_report.xml'
    ],

    'installable': True,
    'application': True,
}
