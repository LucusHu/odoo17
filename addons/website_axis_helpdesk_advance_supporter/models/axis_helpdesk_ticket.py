import re

from odoo import fields, models, api, tools


class AxisHelpdeskTicket(models.Model):
    _inherit = 'axis.helpdesk.ticket'

    team_id = fields.Many2one("axis.helpdesk.ticket.team", "Helpdesk Team", required=True)
    support_user_id = fields.Many2one("res.users", string="Support User", tracking=True, index=True)
    process_hours = fields.Integer('Process Hours', default=0, required=True)
    equipment_number = fields.Char('Equipment Number', required=True)

    # helpdesk_stage_id = fields.Many2one("axis.helpdesk.stage", string="Stage", group_expand="group_helpdesk_stage_ids",
    #                                     default=lambda self: self._default_helpdesk_stage_id(),
    #                                     track_visibility="onchange", ondelete="restrict", index=True, copy=False)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            partner_id = rec.partner_id
            rec.res_user_id = partner_id['engineer_id'] if partner_id and 'engineer_id' in partner_id else False

    # def _default_helpdesk_stage_id(self):
    #     stage_id = self.env.ref('website_axis_helpdesk_advance.axis_helpdesk_stage_new', raise_if_not_found=False)
    #     return stage_id.id
    # def _line_to(self, record):
    #     web_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     web = f'{web_base}/web#id={record.id}&model=axis.helpdesk.ticket&view_type=form'
    #     print(web)
    #     message = f"報修服務通知\r\n"
    #     message += f"客戶：{record.partner_id.name if record.partner_id else 'None'}\r\n"
    #     message += f"單號：{record.number}\r\n"
    #     message += f"狀態：{record.helpdesk_stage_id.name}\r\n"
    #     message += f"設備：{record.equipment_number}\r\n"
    #     message += f"問題：{record.description}\r\n"
    #     message += f"連結：{web}"
    #     if record.res_user_id:
    #         record.res_user_id.line_to(message)
    #     if record.support_user_id:
    #         record.support_user_id.line_to(message)

    # @api.model_create_multi
    # def create(self, list_value):
    #     tickets = super(AxisHelpdeskTicket, self).create(list_value)
    #
    #     for ticket in tickets:
    #         if 'fetchmail_cron_running' in self._context:
    #             ticket._onchange_partner()
    #         if ticket.partner_id:
    #             ticket.message_subscribe(partner_ids=ticket.partner_id.ids)
    #         if ticket.helpdesk_team_id.assigning_method == 'randomly' and ticket.helpdesk_team_id.res_user_ids:
    #             ticket.res_user_id = ticket.helpdesk_team_id.res_user_ids[0].id
    #         if ticket.team_id.assigning_method == 'randomly' and ticket.team_id.res_user_ids:
    #             ticket.res_user_id = ticket.team_id.res_user_ids[0].id
    #         if ticket.res_user_id:
    #             templateq = self.env.ref('website_axis_helpdesk_advance.assigned_request_email_template')
    #             templateq.send_mail(self.id, force_send=True)
    #         ticket.helpdesk_stage_id = self.env["axis.helpdesk.stage"].sudo().search([], limit=1).id
    #
    #     tickets.sudo().helpdesk_sal_policy_apply()
    #     # for vals in list_value:
    #     domain = [('id', '=', tickets.helpdesk_stage_id.id)]
    #     stage_id = self.env['axis.helpdesk.stage'].search(domain)
    #     template = stage_id.mail_template_id
    #     if template:
    #         mail = template.send_mail(tickets.id, force_send=True)
    #
    #     self._line_to(tickets)
    #     return tickets

    # Line 通知

    # def write(self, vals):
    #     super(AxisHelpdeskTicket, self).write(vals)
    #     if vals.get('helpdesk_stage_id'):
    #         stage_id = self.env['axis.helpdesk.stage'].browse(vals.get('helpdesk_stage_id'))
    #         template = stage_id.mail_template_id
    #         if template:
    #             mail = template.send_mail(self.id, force_send=True)
