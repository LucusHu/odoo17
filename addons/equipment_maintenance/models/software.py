from odoo import models, fields


class SoftwareNameType(models.Model):
    _inherit = "type.info"
    _name = "software.name.type"
    _description = "軟體類型"

    name = fields.Char("軟體名稱")
    description = fields.Char("說明")


class InternetType(models.Model):
    _inherit = "type.info"
    _name = "software.internet.type"
    _description = "網型類型"

    name = fields.Char("網型名稱")
    description = fields.Char("說明")


class SoftwareLicense(models.Model):
    _name = "software.license"
    _description = "網路-軟體-授權"

    partner_id = fields.Many2one("res.partner", "客戶")
    name = fields.Many2one("software.name.type", "軟體(服務)名稱", required=True)
    internet_type = fields.Many2one("software.internet.type", "上網型式")

    serial_number = fields.Char("序號")
    contract_expiry_date = fields.Date("合約到期日")
    connection_info = fields.Char("連線資訊")
    account = fields.Char("帳號")
    password = fields.Char("密碼")
    ip_range = fields.Char("IP範圍(寬頻帳號密碼)")
    description = fields.Char("說明")
