from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    subject_remark = fields.Char('付款期間')
