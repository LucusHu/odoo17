from odoo import fields, models, api


# 監控項目: 硬體, smart
class Monitor(models.Model):
    _name = "equipment.monitor.monitor"
    _description = "Monitor Record"

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱")
    hw_id = fields.Many2one("equipment.monitor.hardware", "硬體設備", ondelete='cascade')

    name = fields.Char("代碼", required=True)
    highest = fields.Float("最高值", default=0)
    lowest = fields.Float("最低值", default=0)
    current = fields.Float("目前", default=0)
    type = fields.Selection([("0", "Unknown"), ("1", "效能"), ("2", "溫度"), ("3", "健康度")],
                            "監視類別", default="0")
    count = fields.Integer("發生次數", default=1)
    date_start = fields.Date("監視日期(起)", default=fields.datetime.today())
    date_end = fields.Date("監視日期(迄)", default=fields.datetime.today())

    @api.onchange("hw_id")
    def onchange_hw_id(self):
        for record in self:
            hw_id = record.hw_id
            record.eqpt_id = hw_id.eqpt_id if hw_id else False
