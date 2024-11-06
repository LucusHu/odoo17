from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(default=1)

    @api.onchange('standard_price')
    def onchange_standard_price(self):
        if self.standard_price <= 0:
            raise UserError('價格不正確，請檢查！')
