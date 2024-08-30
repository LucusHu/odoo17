from odoo import fields, models
from random import randint

from odoo.exceptions import UserError


class LineNotifyCategory(models.Model):
    _name = 'line.notify.category'
    _description = 'Notify Tags'

    name = fields.Char('名稱', required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, ondelete='cascade')
    model_name = fields.Char('Model Name', related='model_id.model')
    color = fields.Integer('Color', default=lambda self: self._default_color())
    message = fields.Text('說明')

    def _default_color(self):
        return randint(1, 11)

    def get_message(self, record):
        try:
            message = self.message
            return message.format(**record.read()[0])
        except Exception as ex:
            raise UserError(f'Line Notify 文本異常:{ex}')
