from odoo import models, fields, api


class ConnectType(models.Model):
    _inherit = "type.info"
    _name = "account.connect.type"
    _description = "帳密類型"

    name = fields.Char("帳密名稱")
    description = fields.Char("說明")


# 連線資訊
class AccountConnect(models.Model):
    _inherit = "connect.info"
    _name = "account.connect"
    _description = "連線類型"

    info_id = fields.Many2one("account.info", "帳號密碼")
    name = fields.Many2one("account.connect.type", "類別", required=True)


class AccountInfo(models.Model):
    _name = "account.info"
    _description = "帳號密碼"

    partner_id = fields.Many2one("res.partner", "客戶")
    connect_ids = fields.One2many("account.connect", "info_id", "帳號密碼", ondelete="cascade")

    user_name = fields.Char("使用者")
    connect_name = fields.Char("名稱", compute="_compute_connect")
    connect_account = fields.Char("帳號", compute="_compute_connect")
    active = fields.Boolean("啟用")
    description = fields.Char("說明")
    x_username = fields.Char("x_USERNAME")
    x_email = fields.Char("x_EMAIL")
    x_email_pw = fields.Char("x_EMAIL密碼")
    x_nas_pw = fields.Char("x_NAS密碼")
    x_vpn_pw = fields.Char("x_VPN密碼")

    @api.depends("connect_ids")
    def _compute_connect(self):
        for recode in self:
            # connect_ids = recode.connect_ids.filtered(lambda r: r.active)
            connect_ids = recode.connect_ids
            recode.connect_name = connect_ids[0].name if len(connect_ids) > 0 else False
            recode.connect_account = connect_ids[0].account if len(connect_ids) > 0 else False
        pass
