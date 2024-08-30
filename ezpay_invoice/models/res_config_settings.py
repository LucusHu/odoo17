from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ezpay_demo_mode = fields.Boolean(string='測試模式', help='會使用測試電子發票的API網址進行開票', related='company_id.ezpay_demo_mode', readonly=False)
    # ezpay_MerchantID = fields.Char(string='MerchantID', related='company_id.ezpay_MerchantID', readonly=False)
    # ezpay_HashKey = fields.Char(string='HashKey', related='company_id.ezpay_HashKey', readonly=False)
    # ezpay_HashIV = fields.Char(string='HashIV', related='company_id.ezpay_HashIV', readonly=False)
    # auto_invoice = fields.Selection(string='開立電子發票方式', required=True,
    #                                 selection=[('manual', '手動'), ('automatic', '自動'), ('hand in', '人工填入')],
    #                                 related='company_id.auto_invoice', readonly=False)
    # seller_Identifier = fields.Char(string='賣方統編', related='company_id.seller_Identifier', readonly=False)
    # auto_send_invoice = fields.Boolean(string='自動寄送電子發票', related='company_id.auto_send_invoice',
    #                                    readonly=False)
    ezpay_demo_mode = fields.Boolean(string='測試模式', help='會使用測試電子發票的API網址進行開票')
    ezpay_MerchantID = fields.Char(string='MerchantID')
    ezpay_HashKey = fields.Char(string='HashKey')
    ezpay_HashIV = fields.Char(string='HashIV')

    auto_invoice = fields.Selection(string='開立電子發票方式', required=True,
                                    selection=[('manual', '手動'), ('automatic', '自動'), ('hand in', '人工填入')])
    seller_Identifier = fields.Char(string='賣方統編', related='company_id.seller_Identifier', readonly=False)
    auto_send_invoice = fields.Boolean(string='自動寄送電子發票')
