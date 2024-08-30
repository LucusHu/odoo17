from odoo import fields, models, api


class Lead(models.Model):
    _inherit = "crm.lead"

    @api.onchange("partner_id")
    def onchange_user_id(self):
        # user_id
        self.user_id = self.partner_id.user_id if self.partner_id else False
        # team_id
        self.team_id = self.user_id.sale_team_id if self.user_id else False
