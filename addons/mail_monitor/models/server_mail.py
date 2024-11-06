from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ServerMail(models.Model):
    _inherit = ['mail.thread', ]
    _name = 'mail.monitor.server.mail'
    _description = 'Server Mail'

    name = fields.Char('主旨', required=True)
    content = fields.Html('信件內容', sanitize_attributes=False)
    date = fields.Date('日期', default=fields.Date.today(), readonly=True)
    state = fields.Selection([('0', '未處置'), ('1', '已處置')], '狀態',
                             default='0', required=True)
    filter_ids = fields.Many2many('mail.monitor.server.mail.filter', string='關鍵字', readonly=True)

    # 收信函式
    def message_post(self, **kwargs):
        try:
            self.write({'content': kwargs['body']})
            if self._filter(self):
                self._create_helpdesk(self)
        except Exception as e:
            _logger.info(f"========== message_post Exception start ==========")
            _logger.error(f"Failed to message_post: {e}")
            _logger.info(f"========== message_post Exception end ==========")
        return super(ServerMail, self).message_post(**kwargs)

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
            _logger.info(f"========== _create_helpdesk start ==========")
            name = record.name
            _logger.info(f"name=>{name}")
            if '[' not in name or ']' not in name:
                return False
            inner_content = name[name.index('[') + 1: name.index(']')]
            number, company_name = inner_content.split('_', 1)
            _logger.info(f"number=>{number}")
            _logger.info(f"company_name=>{company_name}")
            tax = number[0:4]
            _logger.info(f"tax=>{tax}")
            equipment_number = number[4:7]
            _logger.info(f"equipment_number=>{equipment_number}")
            content = record.content
            _logger.info(f"content=>{content}")
            # 查詢相關客戶
            # domain = [('vat', 'ilike', tax)]
            # partner_ids = self.env['res.partner'].search(domain)
            # 定義查詢條件
            domain = ['&', '&',
                      ('is_company', '=', True),
                      ('vat', 'ilike', tax[-4:]),
                      ('name', 'ilike', company_name)]  # 避免空值 vat 的問題
            partner_ids = self.env['res.partner'].search(domain)
            # _logger.info(f"len(partners)=>{len(partners)}")
            # # 針對每個 partner 的 VAT 做尾數比對
            # partner_ids = partners.filtered(lambda p: p.vat[-4:] == tax)
            _logger.info(f"len(partner_ids)=>{len(partner_ids)}")
            for partner_id in partner_ids:
                engineer_id = partner_id.engineer_id
                _logger.info(f"engineer_id=>{engineer_id}")
                if not engineer_id:
                    continue
                nas_alarm = partner_id.child_ids.filtered(lambda c: c.name == 'NAS_Alarm')
                _logger.info(f"nas_alarm=>{nas_alarm}")
                nas_alarm = nas_alarm[0] if nas_alarm else False
                if not nas_alarm:
                    continue
                value = {
                    'name': name,
                    'partner_id': nas_alarm.id,
                    'team_id': partner_id.team_id.id,
                    'res_user_id': engineer_id.id,
                    'description': content if content else 'None',
                    'equipment_number': equipment_number,
                }
                _logger.info(f"action=>create")
                self.env['axis.helpdesk.ticket'].create(value)
                _logger.info(f"========== _create_helpdesk end ==========")
            return True  # 如果成功創建記錄，返回 True
        except Exception as e:
            # 處理例外狀況
            _logger.info(f"========== _create_helpdesk Exception start ==========")
            _logger.error(f"Failed to create helpdesk ticket: {e}")
            _logger.info(f"========== _create_helpdesk Exception end ==========")
            return False  # 返回 False 表示失敗

    def action_test(self):
        self.ensure_one()
        for record in self:
            self._create_helpdesk(record)
        # filters = self.env['mail.monitor.server.mail.filter'].search([])
        # if not filters:
        #     return
        # keywords = [(flt.name, flt.id) for flt in filters]
        # for rec in self.search([('date', '=', date.today())]):
        #     if any(kw in rec.name for kw, flt_id in keywords):
        #         # 在這裡處理包含特定字樣的任務
        #         matched_filter_ids = [flt_id for kw, flt_id in keywords if kw in rec.name]
        #         rec.filter_ids = [(6, 0, matched_filter_ids)]
