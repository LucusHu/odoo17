import datetime

from odoo import fields, models, api


class PCAsst(models.Model):
    _name = 'pc.asst'
    _description = 'PC Asst'

    soft_ids = fields.One2many('pc.asst.software', 'pc_id')
    hard_ids = fields.One2many('pc.asst.hardware', 'pc_id')
    nic_ids = fields.One2many('pc.asst.nic', 'pc_id')
    partner_id = fields.Many2one('res.partner', "所屬公司")

    efficacy_id = fields.Many2one('pc.asst.monitor.parameter', "監測效能")
    temperature_id = fields.Many2one('pc.asst.monitor.parameter', "監測溫度")

    guid = fields.Char("編號")
    name = fields.Char("裝置名稱", required=True)
    end_user = fields.Char("客戶端使用者")
    install_date = fields.Date("安裝日期", default=datetime.datetime.today())
    install_user = fields.Many2one('res.users', "安裝人員")


class PCSoft(models.Model):
    _name = 'pc.asst.software'
    _description = 'soft list'

    pc_id = fields.Many2one('pc.asst', "裝置名稱")

    name = fields.Char("軟體名稱", required=True)
    publisher = fields.Date("發行人")
    version = fields.Date("版本")
    install_date = fields.Date("安裝日期", default=datetime.datetime.today())


class PCHard(models.Model):
    _name = 'pc.asst.hardware'
    _description = '硬體資訊'
    # Board, CPU, Memery, HDD, SDD, VGA

    pc_id = fields.Many2one('pc.asst', "裝置名稱")

    name = fields.Char("硬體名稱", required=True)
    brand = fields.Char("品牌")
    frequency = fields.Integer("頻率", default=0)
    speed = fields.Integer("速率", default=0)
    size = fields.Integer("大小", default=0)
    unused = fields.Integer("可用的", default=0)
    used = fields.Integer("已使用", default=0)
    temperature = fields.Float("溫度", default=0)
    efficacy = fields.Float("效能", default=0)
    smart_health = fields.Float("健康度", default=0)
    media_type = fields.Selection([('0', 'Unknown'),
                                   ('1', 'Board'), ('2', 'CPU'), ('3', 'Memery'),
                                   ('4', 'HDD'), ('5', 'SDD'), ('6', 'VGA')],
                                  "硬體類型", required=True, default='0')


class PCNic(models.Model):
    _name = 'pc.asst.nic'
    _description = '網卡資訊'

    pc_id = fields.Many2one('pc.asst', "裝置名稱")

    # name = fields.Char("網卡名稱", required=True)
    mac = fields.Char("MAC", required=True)
    ip = fields.Char("IP")
    interface = fields.Selection([('Wireless80211', 'Wireless80211'), ('Ethernet', 'Ethernet')],
                                 "介面", default='Ethernet')


class PCMonitor(models.Model):
    _name = 'pc.asst.monitor'
    _description = '監視資訊'

    pc_id = fields.Many2one('pc.asst', "裝置名稱")

    name = fields.Char("代碼", required=True)
    highest = fields.Float("最高值", default=0)
    lowest = fields.Float("最低值", default=0)
    current = fields.Float("目前", default=0)
    type = fields.Selection([('0', 'Unknown'), ('1', '效能'), ('2', '溫度'), ('3', '健康度')],
                            "監視類別", default='0')
    count = fields.Integer("發生次數", default=1)
    date = fields.Date("監視日期", default=datetime.datetime.today())


class PCMonitorParameter(models.Model):
    _name = 'pc.asst.monitor.parameter'
    _description = '電腦參數'

    pc_id = fields.Many2one('pc.asst', "裝置名稱")

    interval = fields.Float("監測間隔(分)", default=10)
    allow_count = fields.Integer("容忍次數", default=10)
    value = fields.Float("監測數值", default=90)
    # type = fields.Selection([('efficacy', '效能'), ('temperature', '溫度')], default="temperature")


class PCAlarmParameter(models.Model):
    _name = 'pc.asst.monitor.parameter'
    _description = '電腦參數'

    pc_id = fields.Many2one('pc.asst', "裝置名稱")
