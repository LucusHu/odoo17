import requests
import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gw_demo_mode = fields.Selection([('N', '否'), ('Y', '是')],
                                    '測試模式', default='N', required=True,
                                    help='採測試電子發票網址進行')
    gw_url = fields.Char('Gw url', compute='_compute_url')
    gw_ac = fields.Char('Gw Account')
    gw_pw = fields.Char('Gw Password')
    gw_token = fields.Char('Gw Token')
    gw_date = fields.Datetime('Gw Date')
    gw_key = fields.Char('Gw Key')
    gw_seller_department = fields.Char('Gw SellerDepartment')
    gw_paper_format = fields.Selection([('A5', 'A5格式'), ('A4', 'A4格式')],
                                       '發票格式預設', default='A5', required=True)

    def _compute_url(self):
        test_url = 'https://sstest.gwis.com.tw'
        official_url = 'https://ss.gwis.com.tw'
        for record in self:
            record.gw_url = test_url if (record.gw_demo_mode == 'Y') else official_url

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     return res

    # def set_values(self):
    #     super().set_values()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config = self.env['ir.config_parameter'].sudo()
        res['gw_demo_mode'] = config.get_param('gateweb_invoice.gw_demo_mode')
        res['gw_url'] = config.get_param('gateweb_invoice.gw_url')
        res['gw_ac'] = config.get_param('gateweb_invoice.gw_ac')
        res['gw_pw'] = config.get_param('gateweb_invoice.gw_pw')
        # res['gw_token'] = config.get_param('gateweb_invoice.gw_token')
        # res['gw_date'] = config.get_param('gateweb_invoice.gw_date')
        res['gw_key'] = config.get_param('gateweb_invoice.gw_key')
        res['gw_seller_department'] = config.get_param('gateweb_invoice.gw_seller_department')
        res['gw_paper_format'] = config.get_param('gateweb_invoice.gw_paper_format')
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # 更新配置參數
        config = self.env['ir.config_parameter'].sudo()
        config.set_param('gateweb_invoice.gw_demo_mode', self.gw_demo_mode)
        config.set_param('gateweb_invoice.gw_url', self.gw_url)
        config.set_param('gateweb_invoice.gw_ac', self.gw_ac)
        config.set_param('gateweb_invoice.gw_pw', self.gw_pw)
        # config.set_param('gw_token', self.gw_token)
        # config.set_param('gw_date', self.gw_date)
        config.set_param('gateweb_invoice.gw_key', self.gw_key)
        config.set_param('gateweb_invoice.gw_seller_department', self.gw_seller_department)
        config.set_param('gateweb_invoice.gw_paper_format', self.gw_paper_format)

    def _gw_auth(self, gw_url, _ac, _pw):
        url = f'{gw_url}/api/authenticate'
        headers = {'Content-Type': 'application/json'}
        transaction_data_array = {
            'username': _ac,
            'password': _pw,
            'rememberMe': True,
        }
        response = requests.post(url=url, headers=headers, json=transaction_data_array, timeout=120)
        return response

    def _token(self):
        config = self.env['ir.config_parameter'].sudo()
        url = config.get_param('gateweb_invoice.gw_url')
        ac = config.get_param('gateweb_invoice.gw_ac')
        pw = config.get_param('gateweb_invoice.gw_pw')
        response = self._gw_auth(url, ac, pw)
        if response.status_code == 200:
            response_data = response.json()
            self.env['ir.config_parameter'].sudo().set_param('gateweb_invoice.gw_token', response_data['id_token'])
            self.env['ir.config_parameter'].sudo().set_param('gateweb_invoice.gw_date', datetime.date.today())
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def token(self):
        config = self.env['ir.config_parameter'].sudo()
        token = config.get_param('gateweb_invoice.gw_token')
        date = config.get_param('gateweb_invoice.gw_date')
        if token and date == datetime.date.today():
            return False
        self._token()

    # 開立發票
    def invoice(self, data_array):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        key = config.get_param('gateweb_invoice.gw_key')
        url = f'{gw_url}/api/v1/simplified/C0403?domestic=true&companyKey={key}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.post(url=url, headers=headers, json=data_array, timeout=120)
        return response

    # C0403 Status Instantly
    def invoice_status_instantly(self, identifier, relate_number):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        url = f'{gw_url}/api/v1/invoice/{identifier}/{relate_number}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.get(url=url, headers=headers, timeout=120)
        return response

    # 作廢發票
    def trash(self, data_array):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        key = config.get_param('gateweb_invoice.gw_key')
        url = f'{gw_url}/api/v1/simplified/C0503?domestic=true&companyKey={key}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.post(url=url, headers=headers, json=data_array, timeout=120)
        return response

    # C0503 Status Instantly
    def trash_status_instantly(self, identifier, relate_number):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        url = f'{gw_url}/api/v1/invoiceCancellation/{identifier}/{relate_number}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.get(url=url, headers=headers, timeout=120)
        return response

    # 開立折讓
    def allowance(self, data_array):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        key = config.get_param('gateweb_invoice.gw_key')
        url = f'{gw_url}/api/v1/simplified/D0403?domestic=true&companyKey={key}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.post(url=url, headers=headers, json=data_array, timeout=120)
        return response

    # D0403 Status Instantly
    def allowance_status(self, identifier, original_relate_number, relate_number):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        url = (f'{gw_url}/api/v1/'
               f'simplified/D0403/{original_relate_number}/{identifier}/{relate_number}?completeness=true')
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.get(url=url, headers=headers, timeout=120)
        return response

    # 作廢折讓
    def allowance_trash(self, data_array):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        key = config.get_param('gateweb_invoice.gw_key')
        url = f'{gw_url}/api/v1/simplified/D0503?domestic=true&companyKey={key}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.post(url=url, headers=headers, json=data_array, timeout=120)
        return response

    # D0503 Status Instantly
    def allowance_trash_status(self, identifier, relate_number):
        config = self.env['ir.config_parameter'].sudo()
        gw_url = config.get_param('gateweb_invoice.gw_url')
        token = config.get_param('gateweb_invoice.gw_token')
        url = f'{gw_url}/api/v1/simplified/D0503/{relate_number}/{identifier}?completeness=true'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        response = requests.get(url=url, headers=headers, timeout=120)
        return response
