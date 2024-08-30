from odoo import fields, models
from random import randint


class Filter(models.Model):
    _name = 'mail.monitor.server.mail.filter'
    _description = 'Server Mail Filter'

    name = fields.Char('關鍵字', required=True)
    color = fields.Integer('Color', default=lambda self: self._default_color())
    description = fields.Text('說明')

    def _default_color(self):
        return randint(1, 11)
