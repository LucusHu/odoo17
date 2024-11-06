from odoo import models, fields, api


class InstallRecord(models.Model):
    _name = 'mfp.install.record'
    _description = 'Install Record'

    company_id = fields.Many2one('res.partner', '公司名稱', ondelete='cascade')
    place_id = fields.Many2one('mfp.place', '裝機地點')
    mfp_id = fields.Many2one("mfp.data", '事務機', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', '維護工程師')

    # name = fields.Char()
    company_number = fields.Char('客戶編號', related='company_id.number')
    company_name = fields.Char('公司名稱', related='company_id.name')
    date = fields.Date('日期', default=fields.Date.today())
    count = fields.Integer('次數', default=1, required=True)
    install_place = fields.Char('安裝位置')
    # unknown:0, 安裝:1, 退機:2, 換機[安裝]:3, 換機[退機]:4
    state = fields.Selection([('0', '使用中'), ('1', '新裝機'), ('2', '退機'),
                              ('3', '換機[新裝機]'), ('4', '換機[退機]')],
                             '狀態', default='0', required=True)

    @api.onchange('mfp_id')
    def _onchange_mfp(self):
        mfp_id = self.mfp_id
        if mfp_id:
            self.company_id = mfp_id.company_id
            self.place_id = mfp_id.place_id
