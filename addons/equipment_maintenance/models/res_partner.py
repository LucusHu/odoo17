from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    equipment_ids = fields.One2many("equipment.maintenance", "partner_id", "客戶資訊設備")
    software_ids = fields.One2many("software.license", "partner_id", "客戶軟體授權")
    account_info_ids = fields.One2many("account.info", "partner_id", "帳號密碼")
