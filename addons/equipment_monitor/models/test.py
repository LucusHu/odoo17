from odoo import fields, models, api


class Test(models.Model):
    _name = 'test'
    _description = 'Description'

    name = fields.Char()
