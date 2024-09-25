from odoo import fields, models, api


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    def _line_to(self, record):
        web_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        web = f'{web_base}/web#id={record.id}&model=crm.lead&view_type=form'
        print(web)
        # AAA，您有客戶報價需求：XXXXXX，已開立，請盡速處理
        message = f"{record.user_id.name + '，' if record.user_id else ''}"
        message += f"您有客戶報價需求：{record.name}，已開立，請盡速處理\r\n"
        message += f"連結：{web}"
        if record.user_id:
            record.user_id.line_to(message)

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        self._line_to(record)
        partner_id = record.partner_id
        domain = [('model_name', '=', 'crm.lead')]
        category_id = self.env['line.notify.category'].sudo().search(domain)
        domain = ['&', ('parent_id', '=', partner_id.id), ('notify_ids', 'in', category_id.ids)]
        partner_ids = self.env['res.partner'].sudo().search(domain)

        message = category_id.get_message(record)
        for partner_id in partner_ids:
            partner_id.line_to(message)
        return record
