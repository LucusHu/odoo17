from odoo import fields, models, api


class AccountMoveSend(models.TransientModel):
    _inherit = 'account.move.send'

    # 將 聯絡人 添加至 mail_attachments
    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        partners = super(AccountMoveSend, self)._get_default_mail_partner_ids(move, mail_template, mail_lang)
        partner_id = move.partner_id
        domain = [('model_name', '=', 'account.move')]
        category_id = self.env['line.notify.category'].sudo().search(domain)
        domain = ['&', ('parent_id', '=', partner_id.id), ('notify_ids', 'in', category_id.ids)]
        partners |= self.env['res.partner'].sudo().search(domain)
        return partners
