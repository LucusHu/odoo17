from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._line_to(res)
        return res

    # 建立時, 訊息帶連結
    def _line_to(self, record):
        web_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        web = f'{web_base}/web#id={record.id}&model=project.task&view_type=form'
        print(web)
        # 專案【XXX】已新增
        message = f"專案【{record.name}】已新增\r\n"
        message += f"連結：{web}"

        # 開立專案，要發通知給負責的工程師及專案經理(負責業務)
        if record.user_ids:
            for user_id in record.user_ids:
                user_id.line_to(message)

    def write(self, vals):
        for record in self:
            print(record)
            self._line_to_write(record)
        # 在這裡可以添加你的自定義邏輯
        return super().write(vals)

    def _line_to_write(self, record):
        web_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        web = f'{web_base}/web#id={record.id}&model=project.task&view_type=form'
        print(web)
        # 專案【XXX】狀態已變更為【待處理】
        # 專案【XXX】狀態已變更為【處理中】
        message = f"專案【{record.name}】狀態已變更為【{record.stage_id.name}】\r\n"
        message += f"連結：{web}"

        # 開立專案，要發通知給負責的工程師及專案經理(負責業務)
        if record.user_ids:
            for user_id in record.user_ids:
                user_id.line_to(message)
