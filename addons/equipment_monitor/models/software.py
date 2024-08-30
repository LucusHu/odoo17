from odoo import fields, models


class SoftwareInfo(models.Model):
    _name = 'equipment.monitor.software'
    _description = 'Software'

    eqpt_id = fields.Many2one('equipment.monitor', '裝置名稱', ondelete='cascade')

    name = fields.Char('軟體名稱', required=True)
    publisher = fields.Char('發行人')
    version = fields.Char('版本')
    install_date = fields.Date('安裝日期', default=fields.datetime.today())
