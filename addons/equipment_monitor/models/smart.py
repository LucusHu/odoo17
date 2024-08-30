from odoo import fields, models, api


class SMART(models.Model):
    _name = "equipment.monitor.smart"
    _description = "SMART"

    line_ids = fields.One2many("equipment.monitor.smart.line", "smart_id",
                               "完整明細")
    warning_ids = fields.One2many("equipment.monitor.smart.line", "smart_id",
                                  "故障明細",
                                  domain=[("is_warning", "=", "True")])

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱")
    hw_id = fields.Many2one("equipment.monitor.hardware", "硬體設備", ondelete='cascade')

    date = fields.Date("日期", default=fields.datetime.today())

    @api.onchange("hw_id")
    def onchange_hw_id(self):
        for rec in self:
            hw_id = rec.hw_id
            rec.eqpt_id = hw_id.eqpt_id if hw_id else False


class SMARTLine(models.Model):
    _name = "equipment.monitor.smart.line"

    smart_id = fields.Many2one("equipment.monitor.smart", "SMART", ondelete='cascade')

    name = fields.Char("名稱", required=True)
    value = fields.Integer("數值", default=0)
    # Hazard warning signal
    is_warning = fields.Boolean("故障指示")
