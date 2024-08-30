from datetime import date
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ServerMail(models.Model):
    _name = 'mail.monitor.server.mail'
    _description = 'Server Mail'
    _inherit = ['mail.thread.cc', ]

    name = fields.Char('主旨', required=True)
    content = fields.Html('信件內容', sanitize_attributes=False)
    date = fields.Date('日期', default=fields.Date.today(), readonly=True)
    state = fields.Selection([('0', '未處置'), ('1', '已處置')], '狀態',
                             default='0', required=True)
    filter_ids = fields.Many2many('mail.monitor.server.mail.filter', string='關鍵字', readonly=True)

    # 收信函式
    def _message_post_after_hook(self, message, msg_vals):
        if not self.content:
            self.content = message.body
            super(ServerMail, self)._message_post_after_hook(message, msg_vals)

    @api.model_create_multi
    def create(self, vals_list):
        record = super(ServerMail, self).create(vals_list)
        if self._filter(record):
            self._create_helpdesk(record)
        return record

    # Email 過濾
    def _filter(self, record):
        filters = self.env['mail.monitor.server.mail.filter'].search([])
        if not filters:
            return False
        keywords = [(flt.name, flt.id) for flt in filters]
        if any(kw in record.name for kw, flt_id in keywords):
            # 在這裡處理包含特定字樣的任務
            matched_filter_ids = [flt_id for kw, flt_id in keywords if kw in record.name]
            record.filter_ids = [(6, 0, matched_filter_ids)]
            return record
        return False

    # 開立客服單
    def _create_helpdesk(self, record):
        # 郵件資料
        try:
            name = record.name
            tax = name[1:5]
            equipment_number = name[5:8]
            content = record.content
            # 查詢相關客戶
            domain = [('vat', 'ilike', tax)]
            partner_ids = self.env['res.partner'].search(domain)
            for partner_id in partner_ids:
                engineer_id = partner_id.engineer_id
                if not engineer_id:
                    continue
                value = {
                    'name': name,
                    'partner_id': partner_id.id,
                    'res_user_id': engineer_id.id,
                    'description': content,
                    'equipment_number': equipment_number,
                }
                self.env['axis.helpdesk.ticket'].create(value)
            return True  # 如果成功創建記錄，返回 True
        except Exception as e:
            # 處理例外狀況
            _logger.error(f"Failed to create helpdesk ticket: {e}")
            return False  # 返回 False 表示失敗

    def action_test(self):
        filters = self.env['mail.monitor.server.mail.filter'].search([])
        if not filters:
            return
        keywords = [(flt.name, flt.id) for flt in filters]
        for rec in self.search([('date', '=', date.today())]):
            if any(kw in rec.name for kw, flt_id in keywords):
                # 在這裡處理包含特定字樣的任務
                matched_filter_ids = [flt_id for kw, flt_id in keywords if kw in rec.name]
                rec.filter_ids = [(6, 0, matched_filter_ids)]
