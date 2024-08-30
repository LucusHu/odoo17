from odoo import fields, models


class ConnectInfo(models.Model):
    _name = "connect.info"
    _description = "連線資訊"

    name = fields.Char("名稱")
    ip = fields.Char("位址")
    account = fields.Char("帳號")
    password = fields.Char("密碼")
    description = fields.Text("說明")
    # active = fields.Boolean("啟用", default="1")


class TypeInfo(models.Model):
    _name = "type.info"
    _description = "類型資訊"

    name = fields.Char("名稱")
    description = fields.Text("說明")
