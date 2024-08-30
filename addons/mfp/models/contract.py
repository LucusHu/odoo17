from odoo import fields, models
from random import randint


class Contract(models.Model):
    _name = 'mfp.contract'
    _description = '合約類型'

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char('名稱', required=True)
    color = fields.Integer('Color', default=lambda self: self._default_color())
    description = fields.Text('說明')
    active = fields.Boolean(default=True, help='The active field allows you to hide the contract without removing it.')
