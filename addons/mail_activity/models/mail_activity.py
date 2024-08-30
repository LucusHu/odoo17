from odoo import models, api, _
from odoo.tools import is_html_empty
from odoo.tools.misc import get_lang


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    # 判斷依據, 若無進入網頁則無法確實判斷
    # state = fields.Selection([
    #     ('overdue', 'Overdue'),
    #     ('today', 'Today'),
    #     ('planned', 'Planned'),
    #     ('done', 'Done')], 'State',
    #     compute='_compute_state')

    # 發送郵件並將內容一併發送
    def action_email(self):
        self.ensure_one()
        for activity in self:
            if activity.user_id.lang:
                # Send the notification in the assigned user's language
                activity = activity.with_context(lang=activity.user_id.lang)

            model_description = activity.env['ir.model']._get(activity.res_model).display_name
            body = activity.env['ir.qweb']._render(
                'mail.message_activity_assigned',
                {
                    'activity': activity,
                    'model_description': model_description,
                    'is_html_empty': is_html_empty,
                },
                minimal_qcontext=True
            )
            record = activity.env[activity.res_model].browse(activity.res_id)
            if activity.user_id:
                record.message_notify(
                    partner_ids=activity.user_id.partner_id.ids,
                    body=body,
                    record_name=activity.res_name,
                    model_description=model_description,
                    email_layout_xmlid='mail.mail_notification_layout',
                    subject=_('"%(activity_name)s: %(summary)s" assigned to you',
                              activity_name=activity.res_name,
                              summary=activity.summary or activity.activity_type_id.name),
                    note=activity.note,
                    subtitles=[_('Activity: %s', activity.activity_type_id.name),
                               _('Deadline: %s', activity.date_deadline.strftime(get_lang(activity.env).date_format))]
                )

    @api.model_create_multi
    def create(self, vals_list):
        activities = super(MailActivity, self).create(vals_list)
        message = '溫馨提醒：您已被指派處理事項'
        message += f"{activities.summary}"
        activities.user_id.line_to(message)
        return activities

    def _notify(self, user_id):
        active = []
        overdue = []
        # 篩選符合條件的活動
        filtered_records = self.filtered(lambda activity: activity.date_deadline and activity.user_id.id == user_id.id)
        # 依時間排序
        records = filtered_records.sorted(key=lambda r: r.date_deadline)

        for record in records:
            # 修正時區
            tz = record.user_id.sudo().tz
            date_deadline = record.date_deadline
            record.state = 'done' if not record.active else self._compute_state_from_date(date_deadline, tz)
            if record.state == 'overdue':
                overdue.append(record)
            else:
                active.append(record)

        # 可以根據需要返回或處理 active 和 overdue 列表
        return {
            'active': active,
            'overdue': overdue
        }

    def _send_notify(self):
        user_ids = self.env['res.users'].search([])
        for user_id in user_ids:
            records = self._notify(user_id)
            active_records = records.get('active', [])
            overdue_records = records.get('overdue', [])
            # 处理 active 记录
            active_message = f'溫馨提醒：您今天的待處理事項有\r\n'
            index = 0
            for record in active_records:
                index += 1
                active_message += f"{index}. {record.summary}\r\n"
            if active_records:
                user_id.line_to(active_message)
            # 處理 overdue 紀錄
            overdue_message = f'溫馨提醒：您的行程已過期，請盡速處理\r\n'
            for record in overdue_records:
                overdue_message += f"{index}. {record.summary}\r\n"
            if overdue_records:
                user_id.line_to(overdue_message)
