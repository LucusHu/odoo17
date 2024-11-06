from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    expire_date = fields.Date('Expire Date', compute='_compute_expire_date')
    expire_interval = fields.Integer('Expire Interval', default=1)
    expire_rule_type = fields.Selection([("daily", "Day(s)"),
                                         ("weekly", "Week(s)"),
                                         ("monthly", "Month(s)"),
                                         ("monthlylastday", "Month(s) last day"),
                                         ("quarterly", "Quarter(s)"),
                                         ("semesterly", "Semester(s)"),
                                         ("yearly", "Year(s)")],
                                        'Expire Rule', default='monthly', required=True)

    @api.depends('date_end', 'expire_interval', 'expire_rule_type')
    def _compute_expire_date(self):
        for record in self:
            if not record.date_end:
                record.expire_date = record.date_end
                continue
            internal = record.expire_interval
            if record.expire_rule_type == 'daily':
                record.expire_date = record.date_end + timedelta(days=internal)
            elif record.expire_rule_type == 'weekly':
                record.expire_date = record.date_end + timedelta(weeks=internal)
            elif record.expire_rule_type in ['monthly', 'monthlylastday']:
                record.expire_date = record.date_end + relativedelta(months=internal)
            elif record.expire_rule_type == 'quarterly':
                record.expire_date = record.date_end + relativedelta(months=internal * 3)
            elif record.expire_rule_type == 'semesterly':
                record.expire_date = record.date_end + relativedelta(months=internal * 6)
            elif record.expire_rule_type == 'yearly':
                record.expire_date = record.date_end + relativedelta(years=internal)

    # ========== 排程執行(ir_cron) ==========
    def expire_schedule_start(self):
        _logger.info(f"========== schedule start ==========")
        now = datetime.now().date()
        domain = ['&',
                  ('user_id', '!=', False),
                  ('expire_date', '=', now)]
        records = self.env['contract.contract'].sudo().search(domain)
        for record in records:
            _logger.info(f"name=>{record.partner_id.name}")
            _logger.info(f"user=>{record.user_id.name}")
            _logger.info(f"date=>{record.expire_date}")
            _logger.info(f"internal=>{record.expire_interval}")
            _logger.info(f"rule_type=>{record.expire_rule_type}")
            # 建立活動
            self.create_mail_activity(record)

        _logger.info(f"========== schedule end ==========")

    # ========== mail_activity ==========
    def create_mail_activity(self, record):
        _logger.info(f"========== create mail activity start ==========")
        activity_type = self.env.ref('contract_pivot.mail_activity_data_contract')
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('contract.contract').id,  # 关联的模型
            'res_id': record.id,  # 关联的记录ID
            'activity_type_id': activity_type.id,  # 活动类型，如“待办事项”
            'date_deadline': fields.Date.today(),  # 活动截止日期
            'summary': 'Please review this contract.',  # 活动摘要
            'user_id': record.user_id.id,  # 分配的用户
            'note': 'This is a reminder to follow up on the contract.',  # 详细说明
        })
        _logger.info(f"========== create mail activity end ==========")
