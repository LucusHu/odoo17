from odoo import fields, models, api


class HelpdeskTicket(models.Model):
    _inherit = 'axis.helpdesk.ticket'

    def _line_to(self, record):
        web_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        web = f'{web_base}/web#id={record.id}&model=axis.helpdesk.ticket&view_type=form'
        print(web)
        # 主題：您有新的任務活動
        # 內容：安排活動的內容文字
        message = f"主題：您有新的任務活動\r\n"
        message += f"內容：{record.description}\r\n"
        message += f"連結：{web}"
        if record.res_user_id:
            record.res_user_id.line_to(message)
        if record.support_user_id:
            record.support_user_id.line_to(message)

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        self._line_to(record)
        partner_id = record.partner_id
        domain = [('model_name', '=', 'axis.helpdesk.ticket')]
        category_id = self.env['line.notify.category'].sudo().search(domain)
        domain = ['&', ('parent_id', '=', partner_id.id), ('notify_ids', 'in', category_id.ids)]
        partner_ids = self.env['res.partner'].sudo().search(domain)

        message = category_id.get_message(record)
        for partner_id in partner_ids:
            partner_id.line_to(message)
        return record
