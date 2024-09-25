from odoo import models, fields, api


class ConnectType(models.Model):
    _inherit = 'type.info'
    _name = 'account.connect.type'
    _description = '帳密類型'

    name = fields.Char('帳密名稱')
    description = fields.Text('說明')


# 連線資訊
class AccountConnect(models.Model):
    _inherit = 'connect.info'
    _name = 'account.connect'
    _description = '連線類型'

    info_id = fields.Many2one('account.info', '帳號密碼')
    type_id = fields.Many2one('account.connect.type', '類別', required=True)


class AccountInfo(models.Model):
    _name = 'account.info'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']
    _description = '帳號密碼'

    partner_id = fields.Many2one('res.partner', '客戶')
    company_name = fields.Char('客戶名稱', related='partner_id.name')
    connect_ids = fields.One2many('account.connect', 'info_id', '帳號密碼', ondelete='cascade')

    user_name = fields.Char('使用者')
    connect_name = fields.Char('類別', compute='_compute_connect')
    connect_account = fields.Char('帳號', compute='_compute_connect')
    active = fields.Selection([('0', '否'), ('1', '是')], '啟用',
                              default='1', required=True)
    description = fields.Text('說明')
    x_username = fields.Char('x_USERNAME')
    x_email = fields.Char('x_EMAIL')
    x_email_pw = fields.Char('x_EMAIL密碼')
    x_nas_pw = fields.Char('x_NAS密碼')
    x_vpn_pw = fields.Char('x_VPN密碼')

    @api.depends('connect_ids')
    def _compute_connect(self):
        for recode in self:
            # connect_ids = recode.connect_ids.filtered(lambda r: r.active)
            connect_ids = recode.connect_ids
            connect_name = False
            connect_account = False
            for connect in connect_ids:
                connect_name = connect.type_id.name
                connect_account = connect.account
                break
            recode.connect_name = connect_name
            recode.connect_account = connect_account

    def write(self, vals):
        records = vals.get('connect_ids', [])
        message_body = ''
        changed_fields = []
        removed_fields = []
        for record in records:
            if record[0] == 1:
                ids = record[1]
                data = record[2]
                _record = self.env['account.connect'].browse(ids)
                for key, value in data.items():
                    changed_fields.append("%s: %s -> %s" % (key, _record[key], value))

            if record[0] == 2:
                ids = record[1]
                _record = self.env['account.connect'].browse(ids)
                removed_fields.append("%s/%s" % (_record['account'], _record['password']))

        if changed_fields:
            message_body += "帳號密碼變更:%s" % "\n".join(changed_fields)
        if removed_fields:
            message_body += "帳號密碼刪除:%s" % "\n".join(removed_fields)
        if message_body:
            self.message_post(body=message_body)
        return super(AccountInfo, self).write(vals)
