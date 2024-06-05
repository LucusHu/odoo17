from odoo import fields, models


# 僅記錄網卡資訊
class Nic(models.Model):
    _name = "equipment.monitor.nic"
    _description = "Network interface controller"

    eqpt_id = fields.Many2one("equipment.monitor", "裝置名稱")

    # name = fields.Char("網卡名稱", required=True)
    mac = fields.Char("MAC", required=True)
    ip = fields.Char("IP")
    interface = fields.Selection([("wireless80211", "Wireless80211"), ("ethernet", "Ethernet")],
                                 "介面", default="Ethernet")
    is_active = fields.Boolean("啟用", default="1")
