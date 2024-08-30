from odoo import fields, models


class Action(models.Model):
    _name = "equipment.monitor.action"
    _description = "Action"

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱")

    name = fields.Char("名稱")
    date = fields.Date("日期", default=fields.datetime.today())
