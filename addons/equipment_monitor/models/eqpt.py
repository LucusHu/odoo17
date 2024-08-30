from odoo import fields, models


# 依每台做監控
# (靜態)軟體,硬體(Broad,CPU,VGA,HDD..),網路卡,軟硬體紀錄
# (動態)監控項目 SMART,告警紀錄
class EquipmentMonitor(models.Model):
    _name = 'equipment.monitor'
    _description = 'Equipment Monitor'

    soft_ids = fields.One2many('equipment.monitor.software', 'eqpt_id',
                               '軟體資訊')
    hard_ids = fields.One2many('equipment.monitor.hardware', 'eqpt_id',
                               '硬體資訊')
    nic_ids = fields.One2many('equipment.monitor.nic', 'eqpt_id',
                              '網卡資訊')
    smart_ids = fields.One2many('equipment.monitor.smart', 'eqpt_id',
                                'SMART紀錄')
    monitor_ids = fields.One2many('equipment.monitor.monitor', 'eqpt_id',
                                  '告警紀錄')

    partner_id = fields.Many2one('res.partner', '所屬公司', ondelete='cascade')

    # efficacy_id = fields.Many2one('equipment.monitor.parameter.monitor', '監測效能')
    # temperature_id = fields.Many2one('equipment.monitor.parameter.monitor', '監測溫度')

    guid = fields.Char('編號')
    name = fields.Char('裝置名稱', required=True)
    end_user = fields.Char('客戶端使用者')
    install_date = fields.Date('安裝日期', default=fields.datetime.today())
    install_user = fields.Many2one('res.users', '安裝人員')
    is_active = fields.Boolean('啟用', default='1')
    description = fields.Text('說明')


# 告警資訊
class Notify(models.Model):
    _name = 'equipment.monitor.notify'
    _description = 'Notify'

    eqpt_id = fields.Many2one('equipment.monitor', '裝置名稱', ondelete='cascade')
