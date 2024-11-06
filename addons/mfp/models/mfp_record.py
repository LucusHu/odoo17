from odoo import models, fields, api
from random import randint


class MFPRecordCategory(models.Model):
    _name = 'mfp.record.category'
    _description = '抄表來源'

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char('名稱', required=True)
    color = fields.Integer('Color', default=lambda self: self._default_color())
    active = fields.Boolean(default=True, help='The active field allows you to hide the category without removing it.')


class MFPRecord(models.Model):
    _name = 'mfp.record'
    _description = '抄表紀錄'

    company_id = fields.Many2one('res.partner', '公司名稱', required=True,
                                 domain="['&', '&',"
                                        "('user_ids', '=', False),"
                                        "('company_id', '=', False),"
                                        "('parent_id', '=', False)]", ondelete='cascade')
    company_number = fields.Char('客戶編號', related='company_id.number')
    company_name = fields.Char('公司名稱', related='company_id.name')
    place_id = fields.Many2one('mfp.place', '裝機地點')

    mfp_id = fields.Many2one('mfp.data', '事務機', required=True,
                             domain="[('company_id', '=?', company_id)]", ondelete='cascade')

    @api.onchange('mfp_id')
    def _onchange_mfp(self):
        mfp_id = self.mfp_id
        if mfp_id:
            self.company_id = mfp_id.company_id
            self.place_id = mfp_id.place_id

    user_id = fields.Many2one('res.users', '建立者', default=lambda self: self._default_user_id())

    def _default_user_id(self):
        return self.env.user.id

    # name = fields.Char()
    black_print = fields.Integer('黑白張數', default=0, required=True)
    color_print = fields.Integer('彩色張數', default=0, required=True)
    large_print = fields.Integer('A3張數', default=0, required=True)
    date = fields.Date('抄表日期', default=fields.Date.today(), required=True)
    # unknown:0, 起表:1, 尾表:2, 換機(新機):3, 測試:4
    state = fields.Selection([('0', '一般'), ('1', '起表'), ('2', '尾表'), ('3', '換機'), ('4', '測試')],
                             '狀態', default='0', required=True)
    count = fields.Integer('次數', default=1)
    category_id = fields.Many2many('mfp.record.category', string='來源類別',
                                   default=lambda self: self._default_categories())

    def _default_categories(self):
        return [(6, 0, [self.env.ref('mfp.mfp_record_category_manual').id])]
