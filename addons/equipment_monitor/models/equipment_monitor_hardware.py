from odoo import fields, models, api


# 硬體類別:為了把硬體做分類
class HardwareInfo(models.Model):
    _name = "equipment.monitor.hardware.type"
    _description = "Hardware Info"

    name = fields.Char("名稱", required=True)
    description = fields.Char("描述")


# 各種硬體資訊
# Board, CPU, Memery, HDD, SDD, VGA
class Hardware(models.Model):
    _name = "equipment.monitor.hardware"
    _description = "Hardware"

    smart_ids = fields.One2many("equipment.monitor.smart", "hw_id",
                                "SMART", ondelete="cascade")

    param_ids = fields.One2many("equipment.monitor.monitor.parameter", "hw_id",
                                "閥值設定", ondelete="cascade")

    monitor_ids = fields.One2many("equipment.monitor.monitor", "hw_id",
                                  "監控項目", ondelete="cascade")

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱")
    info_id = fields.Many2one("equipment.monitor.hardware.type", "硬體類型", required=True)

    name = fields.Char("硬體名稱")
    brand = fields.Char("品牌")
    frequency = fields.Integer("頻率", default=0)
    speed = fields.Integer("速率", default=0)
    size = fields.Integer("大小", default=0)
    unused = fields.Integer("可用的", default=0)
    used = fields.Integer("已使用", default=0)
    temperature = fields.Float("溫度", default=0)
    efficacy = fields.Float("效能", default=0)
    smart_health = fields.Float("健康度", default=0)
    is_active = fields.Boolean("啟用", default="1")
    is_notify = fields.Boolean("告警通知", default="1")


# 依照各個硬體做監控(效能,溫度)
class MonitorParameter(models.Model):
    _name = "equipment.monitor.monitor.parameter"
    _description = "Monitor Parameter"

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱",
                              compute="onchange_hw_id", store=True)
    hw_id = fields.Many2one("equipment.monitor.hardware", "硬體設備")

    name = fields.Char("名稱")
    interval = fields.Float("監測間隔(分)", default=10)
    allow_count = fields.Integer("容忍次數", default=10)
    value = fields.Float("監測數值", default=90)
    type = fields.Selection([("performance", "效能"), ("temperature", "溫度")],
                            default="temperature")

    @api.onchange("hw_id")
    def onchange_hw_id(self):
        self.eqpt_id = self.hw_id.eqpt_id if self.hw_id else False
