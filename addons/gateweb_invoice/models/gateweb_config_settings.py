from odoo import models, fields, api


class GateWebConfigSettings(models.Model):
    _name = 'gateweb.config.settings'

    gw_demo_mode = fields.Selection([('N', '否'), ('Y', '是')],
                                    '測試模式', default='N', required=True,
                                    help='採測試電子發票網址進行')
    gw_url = fields.Char('Gw url')
    gw_ac = fields.Char('Gw Account')
    gw_pw = fields.Char('Gw Password')
    gw_token = fields.Char('Gw Token')
    gw_date = fields.Date('Gw Date')
    gw_key = fields.Char('Gw Key')
    gw_seller_department = fields.Char('Gw SellerDepartment')
    gw_paper_format = fields.Selection([('A5', 'A5格式'), ('A4', 'A4格式')],
                                       '發票格式預設', default='A5', required=True)
