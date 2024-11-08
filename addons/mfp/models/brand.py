from odoo import fields, models, api


class Brand(models.Model):
    _name = 'mfp.brand'
    _description = '廠牌'

    line_ids = fields.One2many('mfp.brand.model', 'brand_id', '型號')

    name = fields.Char('名稱', required=True)
    logo = fields.Binary('Logo')
    description = fields.Text('說明')


class BrandModel(models.Model):
    _name = 'mfp.brand.model'
    _description = '廠牌型號'
    _order = 'name asc'

    brand_id = fields.Many2one('mfp.brand', '廠牌', required=True, ondelete='cascade')

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

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.verify == '0':
                name = f'{name} [未驗證]'
            result.append((record.id, name))
        return result
