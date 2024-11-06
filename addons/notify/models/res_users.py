from odoo import fields, models, api
import urllib
import json


class ResUsers(models.Model):
    _inherit = 'res.users'

    line_code = fields.Char("Line Notify Code")
    line_token = fields.Char("Line Notify Token")
    line_notify = fields.Char("odoo服務", compute="_compute_notify")

    # ========== line notify ==========
    # 整理line notify連結
    def _compute_notify(self):
        config = self.env['res.config.settings'].get_values()
        client_id = config.get('client_id')
        redirect_uri = config.get('redirect_uri')

        for rec in self:
            # "https://odoo.cpic.com.tw/callback/notify"
            data = {
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': 'notify',
                'state': f'res_user{rec.id}'
            }
            query_str = urllib.parse.urlencode(data)
            rec.line_notify = f'https://notify-bot.line.me/oauth/authorize?{query_str}'

    # 發送Line 連結
    def action_link(self):
        self.ensure_one()
        # Email 格式
        mail_template = self.env.ref('notify.email_template_res_users_line_notify', raise_if_not_found=False)
        mail_template.send_mail(self.id, email_values={}, force_send=True)
        # compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        #
        # ctx = dict(
        #     default_model='res.users',
        #     default_res_ids=self.ids,
        #     default_template_id=mail_template and mail_template.id or False,
        #     default_composition_mode='comment',
        #     default_email_layout_xmlid="mail.mail_notification_light",
        # )
        # return {
        #     'name': 'Line Notify',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(compose_form.id, 'form')],
        #     'view_id': compose_form.id,
        #     'target': 'new',
        #     'context': ctx,
        # }

    # 發送Line 訊息
    def action_message(self):
        self.line_to(f'{self.name}: 您好,此訊息為測試,請勿回覆')

    # 取得 Token
    def get_token(self, code):
        config = self.env['res.config.settings'].get_values()
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        redirect_uri = config.get('redirect_uri')
        if client_id is None or client_secret is None or redirect_uri is None:
            raise UserWarning('參數設定錯誤')
        url = 'https://notify-bot.line.me/oauth/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=data, headers=headers)
        page = urllib.request.urlopen(req).read()

        res = json.loads(page.decode('utf-8'))
        access_token = res['access_token']
        self.line_token = access_token
        return access_token

    # 發送訊息
    def line_to(self, message):
        access_token = self.line_token
        if not access_token:
            return False
        url = 'https://notify-api.line.me/api/notify'
        headers = {"Authorization": "Bearer " + access_token}

        data = {'message': message}

        data = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=data, headers=headers)
        page = urllib.request.urlopen(req).read()
