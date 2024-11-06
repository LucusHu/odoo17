from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    maintain_user = fields.Many2one('res.users', 'User')
    maintain_start = fields.Date('Date Start')
    maintain_next = fields.Date('Date of Next')
    maintain_end = fields.Date('Date End')
    maintain_internal = fields.Integer('Internal', default=1, required=True)
    maintain_recurring = fields.Selection([("daily", "Day(s)"),
                                           ("weekly", "Week(s)"),
                                           ("monthly", "Month(s)"),
                                           ("monthlylastday", "Month(s) last day"),
                                           ("quarterly", "Quarter(s)"),
                                           ("semesterly", "Semester(s)"),
                                           ("yearly", "Year(s)"), ],
                                          'Recurring', default='monthly', required=True)

    # ========== 排程執行(ir_cron) ==========
    def maintain_schedule_start(self):
        _logger.info(f"========== schedule start ==========")
        now = datetime.now().date()
        domain = ['&',
                  ('maintain_user', '!=', False),
                  ('maintain_start', '!=', False),
                  '|',
                  ('maintain_next', '<=', now),
                  ('maintain_next', '=', False),
                  '|',
                  ('maintain_end', '<=', now),
                  ('maintain_end', '=', False)]
        records = self.env['contract.contract'].sudo().search(domain)
        for record in records:
            _logger.info(f"name=>{record.partner_id.name}")
            _logger.info(f"date=>{record.maintain_next}")
            _logger.info(f"internal=>{record.maintain_internal}")
            _logger.info(f"recurring=>{record.maintain_recurring}")

            # 建立活動
            self.create_mail_activity(record)

            internal = record.maintain_internal
            if not record.maintain_next:
                record.maintain_next = record.maintain_start
            elif record.maintain_recurring == 'daily':
                record.maintain_next = record.maintain_next + timedelta(days=internal)
            elif record.maintain_recurring == 'weekly':
                record.maintain_next = record.maintain_next + timedelta(weeks=internal)
            elif record.maintain_recurring in ['monthly', 'monthlylastday']:
                record.maintain_next = record.maintain_next + relativedelta(months=internal)
            elif record.maintain_recurring == 'quarterly':
                record.maintain_next = record.maintain_next + relativedelta(months=internal * 3)
            elif record.maintain_recurring == 'semesterly':
                record.maintain_next = record.maintain_next + relativedelta(months=internal * 6)
            elif record.maintain_recurring == 'yearly':
                record.maintain_next = record.maintain_next + relativedelta(years=internal)
            _logger.info(f"date of next=>{record.maintain_next}")
        _logger.info(f"========== schedule end ==========")

    # ========== mail_activity ==========
    def create_mail_activity(self, record):
        _logger.info(f"========== create mail activity start ==========")
        # activity_type = self.env.ref('mail.mail_activity_data_todo')  # 活动类型，可以改为其他类型
        activity_type = self.env.ref('contract_maintain.mail_activity_data_repair')
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('contract.contract').id,  # 关联的模型
            'res_id': record.id,  # 关联的记录ID
            'activity_type_id': activity_type.id,  # 活动类型，如“待办事项”
            'date_deadline': fields.Date.today(),  # 活动截止日期
            'summary': '系統通知:定期維護',  # 活动摘要
            'user_id': record.maintain_user.id,  # 分配的用户
            'note': f'定期維護時間已到,請盡快做安排',  # 详细说明
        })
        _logger.info(f"========== create mail activity end ==========")
