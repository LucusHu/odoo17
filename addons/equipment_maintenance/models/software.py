from odoo import models, fields


class SoftwareType(models.Model):
    _inherit = "type.info"
    _name = "software.type"
    _description = "軟體類型"

    name = fields.Char("軟體名稱")
    description = fields.Text("說明")


class InternetType(models.Model):
    _inherit = "type.info"
    _name = "software.internet.type"
    _description = "網型類型"

    name = fields.Char("網型名稱")
    description = fields.Text("說明")


class SoftwareLicense(models.Model):
    _name = "software.license"
    _description = "網路-軟體-授權"

    partner_id = fields.Many2one("res.partner", "客戶")
    company_name = fields.Char('客戶名稱', related='partner_id.name')

    software_type = fields.Many2one("software.type", "軟體類型", required=True)
    internet_type = fields.Many2one("software.internet.type", "上網型式")

    name = fields.Char("軟體名稱", required=True)
    serial_number = fields.Char("序號")
    contract_expiry_date = fields.Date("合約到期日")
    connection_info = fields.Char("連線資訊")
    account = fields.Char("帳號")
    password = fields.Char("密碼")
    ip_range = fields.Char("IP範圍(寬頻帳號密碼)")
    description = fields.Text("說明")
