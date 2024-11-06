from odoo import fields, models, api


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def write(self, values):
        date_start = self.date_start
        res = super().write(values)
        if "stage_id" in values:
            for record in self:
                if record.stage_id:
                    if record.stage_id.type == "in_progress":
                        record.in_progress = True
                        record.date_start = date_start
                    elif record.stage_id.type == "post":
                        record.close_reason_id = False
                        record.in_progress = False
                    else:
                        record.in_progress = False
        return res
