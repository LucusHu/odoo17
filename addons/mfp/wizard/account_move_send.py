from odoo import fields, models, api


class AccountMoveSend(models.TransientModel):
    _inherit = 'account.move.send'

    # 建立 mail_template 的 attachment 物件
    def _get_mail_template_attachments_mfp(self, move, mail_template):
        """ Returns all the placeholder data and mail template data
        """
        domain = [('name', '=',  f'事務機明細{move.name.replace("/", "_")}.pdf')]
        attachments = self.env['ir.attachment'].sudo().search(domain)
        return [
            {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'placeholder': False,
                'mail_template_id': mail_template.id,
            }
            for attachment in attachments
        ]

    # 將 attachment 添加至 mail_attachments
    def _get_default_mail_attachments_widget(self, move, mail_template):
        result = super(AccountMoveSend, self)._get_default_mail_attachments_widget(move, mail_template)
        result += self._get_mail_template_attachments_mfp(move, mail_template)
        return result
