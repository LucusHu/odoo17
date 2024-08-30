from odoo import fields, models, api


class Brand(models.Model):
    _name = 'mfp.brand'
    _description = '廠牌'

    line_ids = fields.One2many('mfp.brand.model', 'brand_id', '型號', ondelete='cascade')

    name = fields.Char('名稱', required=True)
    logo = fields.Binary('Logo')
    description = fields.Text('說明')


class BrandModel(models.Model):
    _name = 'mfp.brand.model'
    _description = '廠牌型號'

    brand_id = fields.Many2one('mfp.brand', '廠牌', required=True)

    brand_name = fields.Char('廠牌名稱', related='brand_id.name')
    name = fields.Char('機器型號', required=True)
    code = fields.Integer('機器編號', readonly=True)
    verify = fields.Selection([('0', '未驗證'), ('1', '已驗證')],
                              '驗證', default='0', readonly=True)
    feature = fields.Char('功能')
    logo = fields.Binary('Logo')
    description = fields.Text('說明')
    state = fields.Selection([('0', '停用'), ('1', '啟用')],
                             '狀態', default='1', required=True)

    @api.depends('name')
    def name_get(self):
        rec = []
        for records in self:
            name = records.name
            verify = records.verify
            if verify == '0':
                name = f'{name}[未驗證]'
            rec.append((records.id, name))
        return rec
