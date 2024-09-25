from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EquipmentType(models.Model):
    _inherit = 'type.info'
    _name = 'equipment.device.type'
    _description = '設備類型'

    name = fields.Char('設備名稱')
    description = fields.Text('說明')


class RemoteType(models.Model):
    _inherit = 'type.info'
    _name = 'equipment.remote.type'
    _description = '遠端類型'

    name = fields.Char('遠端名稱')
    description = fields.Text('說明')


# 遠端連線
class RemoteConnect(models.Model):
    _inherit = 'connect.info'
    _name = 'remote.connect'
    _description = '遠端連線'

    info_id = fields.Many2one('equipment.maintenance', '設備')
    type_id = fields.Many2one('equipment.remote.type', '類別', required=True)


class Equipment(models.Model):
    _name = 'equipment.maintenance'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']
    _description = '資訊設備'

    # 唯一值
    _sql_constraints = [
        ('unique_partner_number', 'UNIQUE(partner_id, number)', '同一客戶下的設備編號必須唯一!')
    ]

    partner_id = fields.Many2one('res.partner', '客戶')
    company_name = fields.Char('客戶名稱', related='partner_id.name')

    remote_ids = fields.One2many('remote.connect', 'info_id', '遠端連線', ondelete='cascade')

    name = fields.Char('設備名稱', required=True)
    number = fields.Char('設備編號', required=True)
    type = fields.Many2one('equipment.device.type', '設備類型', required=True)
    serial_number = fields.Char('設備序號')

    user = fields.Char('使用者')
    account = fields.Char('帳號')
    password = fields.Char('密碼')

    brand_model = fields.Char('廠牌型號')
    ip_address = fields.Char('IP位址')

    contract_subject = fields.Selection([('0', '否'), ('1', '是')], '合約標的',
                                        default='1', required=True)
    os_firmware_version = fields.Char('作業系統-韌體版本')
    device_description = fields.Text('裝置說明')
    backup_description = fields.Text('備份說明')

    x_remote_connection = fields.Char('x_遠端連線')

    @api.constrains('partner_id', 'number')
    def _check_unique_partner_number(self):
        for equipment in self:
            if equipment.partner_id and equipment.number:
                duplicate_equipment = self.env['equipment.maintenance'].search([
                    ('partner_id', '=', equipment.partner_id.id),
                    ('number', '=', equipment.number),
                    ('id', '!=', equipment.id),
                ])
                if duplicate_equipment:
                    raise ValidationError('同一客戶下的設備編號必須唯一!')

    def write(self, vals):
        records = vals.get('remote_ids', [])
        message_body = ''
        changed_fields = []
        removed_fields = []
        for record in records:
            if record[0] == 1:
                ids = record[1]
                data = record[2]
                _record = self.env['remote.connect'].browse(ids)
                for key, value in data.items():
                    changed_fields.append("%s: %s -> %s" % (key, _record[key], value))

            if record[0] == 2:
                ids = record[1]
                _record = self.env['remote.connect'].browse(ids)
                removed_fields.append("%s/%s/%s" % (_record['ip'], _record['account'], _record['password']))

        if changed_fields:
            message_body += "遠端連線變更:%s" % "\n".join(changed_fields)
        if removed_fields:
            message_body += "遠端連線刪除:%s" % "\n".join(removed_fields)
        if message_body:
            self.message_post(body=message_body)
        return super(Equipment, self).write(vals)
