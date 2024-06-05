from odoo import fields, models, api


class SMART(models.Model):
    _name = "equipment.monitor.smart"
    _description = "SMART"

    line_ids = fields.One2many("equipment.monitor.smart.line", "smart_id",
                               "完整明細", ondelete="cascade")
    warning_ids = fields.One2many("equipment.monitor.smart.line", "smart_id",
                                  "故障明細", ondelete="cascade",
                                  domain=[("is_warning", "=", "True")])

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱",
                              compute="onchange_hw_id", store=True)
    hw_id = fields.Many2one("equipment.monitor.hardware", "硬體設備")

    date = fields.Date("日期", default=fields.datetime.today())

    @api.onchange("hw_id")
    def onchange_hw_id(self):
        self.eqpt_id = self.hw_id.eqpt_id if self.hw_id else False


class SMARTLine(models.Model):
    _name = "equipment.monitor.smart.line"

    smart_id = fields.Many2one("equipment.monitor.smart", "SMART")

    name = fields.Char("名稱", required=True)
    value = fields.Integer("數值", default=0)
    # Hazard warning signal
    is_warning = fields.Boolean("故障指示")
