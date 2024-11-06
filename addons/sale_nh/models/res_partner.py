from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        # 添加 name、phone 和 mobile 的搜索条件
        domain = ['|', '|',
                  ('name', operator, name),
                  ('phone', operator, name),
                  ('mobile', operator, name)]

        partners = self.search(args + domain, limit=limit)
        return partners.name_get()
