import base64

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    print_ids = fields.One2many('account.print.line', 'move_id', '事務機明細', ondelete='cascade')
    # mfp_id = fields.Many2one('mfp.data', '事務機')
    # # year = fields.Integer(string='年份')
    # # month = fields.Integer(string='月份')
    # account_type = fields.Selection([('0', '一般'), ('1', '事務機')],
    #                                 default='0')

    # ========== Line ==========
    def action_line_record(self):
        if not self.mfp_id or not self.mfp_id.accountant_ids:
            return
        company_id = self.mfp_id.company_id
        # partner 聯絡人
        accountant_ids = self.mfp_id.accountant_ids
        for partner_id in accountant_ids:
            partner_id.line_to(f'{company_id.name}通知貴公司帳單已寄出,請至電子信箱收件與確認')

    # ========== 電子發票 ==========
    # def get_ref(self, xml_id):
    #     return self.env.ref(xml_id)
    def get_report_pdf(self, xml_id):
        ref_id = self.env.ref(xml_id)
        # _render_qweb_pdf 是引用 ir.actions.report 因此僅限制 ir.actions.report 使用
        return ref_id._render_qweb_pdf(self.id) if ref_id else False

    def report_gateweb_invoice(self):
        # report_id = self.get_ref('ezpay_invoice.action_print_ezpay_invoice')
        # if not report_id:
        #     return
        # generated_report = report_id._render_qweb_pdf(self.id)
        generated_report = self.get_report_pdf('gateweb_invoice.report_gateweb_invoice')
        if not generated_report:
            return
        data_record = base64.b64encode(generated_report[0])
        ir_values = {
            'name': '電子發票',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'account.move',
        }
        return self.env['ir.attachment'].sudo().create(ir_values)

    def report_mfp_detail(self):
        generated_report = self.get_report_pdf('mfp.action_report_account_move')
        if not generated_report:
            return
        data_record = base64.b64encode(generated_report[0])
        ir_values = {
            'name': '事務機明細',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'account.move',
        }
        return self.env['ir.attachment'].sudo().create(ir_values)

    def send_email(self):
        attachment_ids = [(5, 0, 0)]

        # 建立附件
        reports = [
            self.report_gateweb_invoice(),
            self.report_mfp_detail()
        ]
        for report in reports:
            if report:
                attachment_ids.append((4, report.id))

        # 獲取郵件模板
        email_template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)

        # 如果郵件模板存在，設置附件
        if email_template:
            email_template.attachment_ids = attachment_ids

        return email_template

    def action_invoice_sent(self):
        self.ensure_one()
        template = self.send_email()
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout='mail.mail_notification_paynow',
            model_description=self.with_context(lang=False).type_name,
            force_email=True,
            active_ids=self.ids,
        )

        report_action = {
            'name': 'Send Invoice',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        self.action_line_record()
        return report_action
        # return super(AccountMove, self).action_invoice_sent()


class AccountPrintLine(models.Model):
    _name = 'account.print.line'
    _description = 'Account Print Line'

    move_id = fields.Many2one('account.move', 'Journal Entry')
    mfp_id = fields.Many2one('mfp.data', '事務機', required=True)
    number = fields.Char('客戶編號', related='mfp_id.company_number')
    # rental = fields.Integer('租金', related='mfp_id.rental')
    rental = fields.Integer('租金')
    # 租金*週期=總月租費用
    # 贈送張數*週期=總贈送張數
    # pay_period = fields.Selection([('1', '每月'), ('2', '兩個月'), ('3', '每季(三個月)'),
    #                                ('6', '半年'), ('12', '每年')],
    #                               '結算期數')
    pay_period = fields.Selection(string='結算期數', related='mfp_id.pay_period')
    contract_ids = fields.Many2many(string='合約類型', related='mfp_id.contract_ids')

    date_start = fields.Date('起算日期', required=True, default=fields.Date.today())
    date_end = fields.Date('結算日期', required=True, default=fields.Date.today())

    # 租金*週期=總月租費用
    # 贈送張數*週期=總贈送張數
    period = fields.Integer('月份期數', default=0, required=True)
    description = fields.Html('備註')

    # ==== 黑白 ====
    black_print_start = fields.Integer('黑白-起算張數')
    black_print_end = fields.Integer('黑白-結算張數')
    black_print_invalid = fields.Integer('黑白-作廢張數')
    black_print_overprice = fields.Float('黑白-超印價格', related='mfp_id.black_print_overprice')
    black_print_deduct = fields.Integer('黑白-贈送張數', related='mfp_id.black_print_deduct')
    black_print_number = fields.Integer('黑白-列印張數', compute='_compute_black_print_count')
    black_print_count = fields.Integer('黑白-列印張數', compute='_compute_black_print_count', store=True)
    # ==== 彩色 ====
    color_print_start = fields.Integer('彩色-起算張數')
    color_print_end = fields.Integer('彩色-結算張數')
    color_print_invalid = fields.Integer('彩色-作廢張數')
    color_print_overprice = fields.Float('彩色-超印價格', related='mfp_id.color_print_overprice')
    color_print_deduct = fields.Integer('彩色-贈送張數', related='mfp_id.color_print_deduct')
    color_print_number = fields.Integer('彩色-列印張數', compute='_compute_color_print_count')
    color_print_count = fields.Integer('彩色-列印張數', compute='_compute_color_print_count', store=True)
    # ==== 大張 ====
    large_print_start = fields.Integer('A3-起算張數')
    large_print_end = fields.Integer('A3-結算張數')
    large_print_invalid = fields.Integer('A3-作廢張數')
    large_print_overprice = fields.Float('A3-超印價格', related='mfp_id.large_print_overprice')
    large_print_number = fields.Integer('A3-列印張數', compute='_compute_large_print_count')
    large_print_count = fields.Integer('A3-列印張數', compute='_compute_large_print_count', store=True)

    @api.onchange('mfp_id')
    def _onchange_mfp(self):
        mfp_id = self.mfp_id
        if mfp_id:
            # self.company_id = mfp_id.company_id
            self.rental = mfp_id.rental
            # self.pay_period = mfp_id.pay_period

    @api.depends('black_print_start', 'black_print_end', 'black_print_deduct', 'black_print_invalid')
    def _compute_black_print_count(self):
        for rec in self:
            # mfp_id = rec.mfp_id
            period = rec.period
            # period = int(mfp_id.pay_period) if mfp_id.pay_period else 1
            end = rec.black_print_end if rec.black_print_end else 0
            start = rec.black_print_start if rec.black_print_start else 0
            deduct = rec.black_print_deduct if rec.black_print_deduct else 0
            invalid = rec.black_print_invalid if rec.black_print_invalid else 0
            count = end - start - (deduct * period) - invalid
            rec.black_print_count = count
            rec.black_print_number = end - start

    @api.depends('color_print_start', 'color_print_end', 'color_print_deduct', 'color_print_invalid')
    def _compute_color_print_count(self):
        for rec in self:
            # mfp_id = rec.mfp_id
            period = rec.period
            # period = int(mfp_id.pay_period) if mfp_id.pay_period else 1
            end = rec.color_print_end if rec.color_print_end else 0
            start = rec.color_print_start if rec.color_print_start else 0
            deduct = rec.color_print_deduct if rec.color_print_deduct else 0
            invalid = rec.color_print_invalid if rec.color_print_invalid else 0
            count = end - start - (deduct * period) - invalid
            rec.color_print_count = count
            rec.color_print_number = end - start

    @api.depends('large_print_start', 'large_print_end', 'large_print_invalid')
    def _compute_large_print_count(self):
        for rec in self:
            # mfp_id = rec.mfp_id
            # period = rec.period
            # period = int(mfp_id.pay_period) if mfp_id.pay_period else 1
            end = rec.large_print_end if rec.large_print_end else 0
            start = rec.large_print_start if rec.large_print_start else 0
            # deduct = rec.large_print_deduct
            invalid = rec.large_print_invalid if rec.large_print_invalid else 0
            count = end - start - invalid
            rec.large_print_count = count
            rec.large_print_number = end - start