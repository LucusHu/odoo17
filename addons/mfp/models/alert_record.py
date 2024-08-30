from odoo import fields, models


class AlertRecord(models.Model):
    _name = 'mfp.alert.record'
    _description = '告警訊息'

    mfp_id = fields.Many2one('mfp.data', '事務機', ondelete='cascade')

    code = fields.Integer('代碼')
    description = fields.Char('訊息')
    date = fields.Date('回報日期', default=fields.Date.today())
    state = fields.Selection([('0', '一般'), ('1', '嚴重')],
                             '狀態', default='0', required=True)
