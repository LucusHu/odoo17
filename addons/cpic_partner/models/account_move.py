from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_no = fields.Char("發票號碼")
