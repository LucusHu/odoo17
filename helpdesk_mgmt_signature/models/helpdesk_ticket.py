# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.depends('stage_id')
    def _compute_stage_url(self):
        for rec in self:
            rec.stage_url = ''
            if rec.stage_id.name == '已結案':
                web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                rec.stage_url = web_base_url + rec._get_share_url()

    signature = fields.Image(string='簽名', copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char('簽名者', help='在服務單據上簽名的人的姓名。', copy=False)
    signed_on = fields.Datetime('簽名時間', help='Date of the signature.', copy=False)
    stage_url = fields.Char(string='結案URL', compute="_compute_stage_url")
