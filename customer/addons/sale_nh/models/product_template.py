from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    second_name = fields.Char('Second Name')
    health_code = fields.Char('Health Code')
    health_price = fields.Float('Health Price')
    materials = fields.Text('Materials')
