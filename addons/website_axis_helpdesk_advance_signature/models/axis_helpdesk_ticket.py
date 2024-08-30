from odoo import api, fields, models


class AxisHelpDeskTicket(models.Model):
    _inherit = 'axis.helpdesk.ticket'

    @api.depends('helpdesk_stage_id')
    def _compute_stage_url(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.stage_url = ''
            # Done (已結案)
            if record.helpdesk_stage_id.sequence == 5:
                record.stage_url = web_base_url + f'/axis/helpdesk/ticket/{record.ids[0]}{"/" + record.access_token if record.access_token else ""}'

    signature = fields.Image(string='簽名', copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char('簽名者', help='在服務單據上簽名的人的姓名。', copy=False)
    signed_on = fields.Datetime('簽名時間', help='Date of the signature.', copy=False)
    stage_url = fields.Char(string='結案URL', compute="_compute_stage_url")
