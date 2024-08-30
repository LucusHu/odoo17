from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        res = super(AccountMove, self).action_invoice_sent()
        for record in self:
            partner_id = record.partner_id
            domain = [('model_name', '=', 'account.move')]
            category_id = self.env['line.notify.category'].sudo().search(domain)
            domain = ['&', ('parent_id', '=', partner_id.id), ('notify_ids', 'in', category_id.ids)]
            partner_ids = self.env['res.partner'].sudo().search(domain)

            message = category_id.get_message(record)
            for partner_id in partner_ids:
                partner_id.line_to(message)
        return res

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #     print(records)
    #
    #     # 在這裡可以添加你的自定義邏輯
    #     # 公司
    #     partner_id = records.partner_id
    #     domain = [('model_name', '=', 'account.move')]
    #     category_id = self.env['line.notify.category'].sudo().search(domain)
    #     domain = ['&', ('parent_id', '=', partner_id.id), ('notify_ids', 'in', category_id.ids)]
    #     partner_ids = self.env['res.partner'].sudo().search(domain)
    #
    #     message = category_id.get_message(records)
    #     for partner_id in partner_ids:
    #         partner_id.line_to(message)
    #     return records
    #
    # def write(self, vals):
    #     records = super().write(vals)
    #     print(records)
    #     # 在這裡可以添加你的自定義邏輯
    #     return records
