from odoo import fields, models, api


class Place(models.Model):
    _name = 'mfp.place'
    _description = 'Place'

    company_id = fields.Many2one('res.partner', '公司名稱',
                                 domain="[('parent_id', '=', False)]",
                                 required=True, ondelete='cascade')

    code = fields.Char(string='Code')
    name = fields.Char('裝機地點', default='辦公室', required=True)
    install_place = fields.Char('驅動安裝位置')
    state = fields.Selection([('0', '未啟用'), ('1', '啟用'), ('2', '停用')],
                             '狀態', default='1', required=True)
    description = fields.Text('描述')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'code' not in vals or not vals['code']:
                # 沒有代碼，給予一個新代碼
                vals['code'] = self.env['ir.sequence'].next_by_code('mfp.place.sequence')
                while True:
                    domain = [('code', '=', vals['code'])]
                    places = self.env['mfp.place'].search(domain)
                    if len(places) == 0:
                        break
                    vals['code'] = self.env['ir.sequence'].next_by_code('mfp.place.sequence')
        return super(Place, self).create(vals_list)
