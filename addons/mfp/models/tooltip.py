from odoo import fields, models
from random import randint


class Tooltip(models.Model):
    _name = 'mfp.tooltip'
    _description = '訊息提示'

    name = fields.Char('名稱', required=True)
    color = fields.Integer('Color', default=lambda self: self._default_color())

    def _default_color(self):
        return randint(1, 11)
