from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_no = fields.Char("發票號碼")
