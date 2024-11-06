import base64
import datetime

from .qrcode_encrypter import QRCodeEncrypter
from odoo import fields, models, api
from odoo.exceptions import UserError


class GateWebInvoice(models.Model):
    _inherit = 'account.move'
    _description = '關網電子發票'

    detail_ids = fields.One2many('account.move.line', compute='_compute_detail_ids')

    @api.depends('line_ids')
    def _compute_detail_ids(self):
        for record in self:
            record.detail_ids = record.line_ids.filtered(lambda la: la.display_type == 'product')

    #
    # allowance_ids = fields.One2many('gateweb.invoice.allowance', 'invoice_id',
    #                                 '折讓單', ondelete='cascade')
    # ========== 自定義 custom ==========
    invoice_category = fields.Selection([('B2B', 'B2B'), ('B2C', 'B2C')],
                                        '發票類別', default='B2B', required=True)
    invoice_paper = fields.Selection([('A5', 'A5格式'), ('A4', 'A4格式')],
                                     '發票格式', default=lambda self: self._default_invoice_paper(), required=True)

    def _default_invoice_paper(self):
        # self.company_id 起初是沒有數值的 因此採 self.env.company
        config = self.env['ir.config_parameter'].sudo()
        return config.get_param('gateweb_invoice.gw_paper_format')

    invoice_state = fields.Selection([('not invoiced', '未開立'),
                                      ('uploading', '待上傳'), ('invoiced', '已開立'),
                                      ('allowance', '已折讓'),
                                      ('canceling', '待作廢'), ('canceled', '已作廢')],
                                     '電子發票狀態', default='not invoiced', readonly=True)
    # allowance_amount = fields.Monetary('剩餘可折讓金額', compute='_compute_allowance_amount', store=True)

    # def _get_paperformat_id(self):
    #     paperformat_a5 = self.env.ref('gateweb_invoice.paperformat_gateweb_invoice_A5')
    #     paperformat_a4 = self.env.ref('gateweb_invoice.paperformat_gateweb_invoice_A4')
    #     return paperformat_a5.id if self.invoice_paper == 'A5' else paperformat_a4.id

    # ========== invoice ==========
    # 待回傳後, 再行增添
    # invoice_no = fields.Char('發票號碼')
    invoice_number = fields.Char('發票號碼')
    gw_invoice_date = fields.Date('發票開立日期', readonly=True)
    invoice_time = fields.Char('發票開立時間', readonly=True)

    # ========== 賣方資訊 ==========
    seller_identifier = fields.Char('賣方統編', compute='_compute_seller')
    # 必須為繁體中文（財政部登記姓名一致）
    seller_name = fields.Char('賣方公司名稱', readonly=True)
    # 該欄位值由關網提供＆若為子母公司設定，依照不同公司之印表機名稱代入
    seller_department = fields.Char('印表機名稱')
    # 必須為繁體中文（財政部登記一致）
    seller_address = fields.Char('賣方營業登記地址', readonly=True)

    def _compute_seller(self):
        for rec in self:
            seller = rec.invoice_user_id.company_id
            rec.seller_identifier = seller.vat
            rec.seller_name = seller.name
            rec.seller_address = ('%s%s%s%s' % (
                seller.state_id.name if seller.state_id else '',
                seller.city if seller.city else '',
                seller.street if seller.street else '',
                seller.street2 if seller.street2 else '',))

    def _default_seller_identifier(self):
        seller = self.env.user.company_id
        return seller.vat

    def _default_seller_name(self):
        seller = self.env.user.company_id
        return seller.name

    def _default_seller_address(self):
        seller = self.env.user.company_id
        return ('%s%s%s%s' % (
            seller.state_id.name if seller.state_id else '',
            seller.city if seller.city else '',
            seller.street if seller.street else '',
            seller.street2 if seller.street2 else '',))

    # seller_person_incharge = fields.Char('賣方負責人')
    # seller_telephone_number = fields.Char('賣方電話')
    # seller_facsimile_number = fields.Char('賣方傳真')
    # seller_email_address  = fields.Char('賣方電子郵件地址')
    # seller_customer_number = fields.Char('賣方號碼')
    # seller_role_remark = fields.Char('發票總備註')

    # ========== 買方資訊 ==========
    # 非營業人固定放0000000000
    buyer_identifier = fields.Char('買方統一編號', compute='_compute_buyer')
    # 非營業人固定放0000000000
    buyer_name = fields.Char('買方公司名稱', readonly=True)
    # buyer_address = fields.Char('買方營業地址')
    # buyer_person_incharge = fields.Char('買方負責人')
    # buyer_telephone_number = fields.Char('買方電話')
    # buyer_facsimile_number = fields.Char('買方傳真')
    # B2B，若需要發送E-Mail PDF檔，將買方信箱郵件地址放上
    buyer_email_address = fields.Char('買方電子郵件地址')

    @api.depends('partner_id')
    def _compute_buyer(self):
        for record in self:
            buyer = record.partner_id.parent_id if record.partner_id.parent_id else record.partner_id
            record.buyer_identifier = buyer.vat if buyer else False
            record.buyer_name = buyer.name if buyer else False

    # @api.depends('partner_id')
    # def _onchange_buyer(self):
    #     for record in self:
    #         buyer = record.partner_id.parent_id if record.partner_id.parent_id else record.partner_id
    #         record.buyer_identifier = buyer.vat
    #         record.buyer_name = buyer.name
    # self.buyer_email_address = self.partner_id.email if self.partner_id else False

    # buyer_customer_number = fields.Char('買方號碼')
    # 若有值顯示於發票備註欄位
    # buyer_role_remark = fields.Char('發票總備註')
    # 待回傳後, 再行增添
    # 作廢日期(YYYYMMDD)

    # 未填值則由關網自動產生填入
    # random_number = fields.Char('發票防偽隨機碼')
    # 必須是一組唯一的編號，可以是內部訂單號碼或自訂規則之編碼，未來查詢發票及異動對應使用
    # 在此與 sale_order name 同名
    relate_number = fields.Char('發票唯一號碼', readonly=True)
    invoice_type = fields.Selection([('07', '一般稅額'), ('08', '特種稅額')],
                                    '發票類別', default='07')
    # ※B2C STORAGE專用:
    # 3J0002：手機條碼
    # CQ0001：自然人憑證
    # EJ0110：關網會員(限定企業用戶專用)
    carrier_type = fields.Selection([('3J0002', '手機條碼'), ('CQ0001', '自然人憑證'),
                                     ('EJ0110', '關網會員(限定企業用戶專用)')],
                                    '載具類別代號')
    # carrierType: EJ0110  則放入email format: EJ0110  則放入email format
    # 載具顯碼
    carrier_id1 = fields.Char('載具號碼')
    carrier_id2 = fields.Char('載具隱碼')

    print_mark = fields.Selection([('Y', '是'), ('N', '否')],
                                  '索取紙本發票', default='Y', required=True)
    donate_mark = fields.Selection([('1', '是'), ('0', '否')],
                                   '捐贈發票', default='0', required=True)
    # 受贈單位代碼donateMark is 1 , npoban 必填3-7碼數字
    npo_ban = fields.Char("捐贈碼")

    # ========== 金額資訊(稅額) ==========
    sales_amount = fields.Integer('銷售額(應稅)', default=0)
    free_tax_sales_amount = fields.Integer('銷售額(免稅)', default=0)
    zero_tax_sales_amount = fields.Integer('銷售額(零稅率)', default=0)
    tax_type = fields.Selection([('1', '應稅'), ('2', '免稅'), ('3', '零稅率')],
                                '課稅別', default='1', required=True)
    # tax Type(1)=0.05、tax Type(2、3)= 0 、tax Type=(3) CustomsClearanceMark必填

    tax_rate = fields.Float('稅率', compute='_compute_tax_rate')

    @api.depends('tax_type')
    def _compute_tax_rate(self):
        for record in self:
            if record.tax_type == '1':
                record.tax_rate = 0.05
            else:
                record.tax_rate = 0

    # 1: 非經海關出口   2:經海關出口
    customs_clearance_mark = fields.Selection([('1', '非經海關出口'), ('2', '經海關出口')],
                                              '零稅率通關方式', default='1')

    allowance_relate_number = fields.Char('折讓單唯一號碼', readonly=True)
    allowance_date = fields.Date('折讓日期', readonly=True)
    allowance_time = fields.Char('折讓時間', readonly=True)

    # amount_tax
    # tax_amount = fields.Integer('營業稅額')

    # totalAmount = salesAmount + free_tax_sales_amount + zero_tax_sales_amount + tax_amount
    # amount_total
    # total_amount = fields.Integer('總計金額')

    # ========== 作廢資訊 ==========
    cancel_date = fields.Date('作廢日期', readonly=True)
    # 作廢時間(HH: mm:ss)
    cancel_time = fields.Char('作廢時間', readonly=True)
    # 作廢原因
    cancel_reason = fields.Text('作廢原因')

    # @api.depends('allowance_ids')
    # def _compute_allowance_amount(self):
    #     for record in self:
    #         detail_ids = record.allowance_ids
    #         amount_total = record.amount_total
    #         tax = 0
    #         amount = 0
    #         for line in detail_ids:
    #             amount += line.amount if line.state != 'canceled' else 0
    #             tax += line.tax if line.state != 'canceled' else 0
    #         if amount_total < (amount + tax):
    #             raise UserError('折讓金額已超出')
    #         record.allowance_amount = amount_total - (amount + tax)

    @api.onchange('tax_type')
    def _onchange_tax_rate(self):
        self.tax_rate = 0.05 if self.tax_type == '1' else 0

    # ==================== 發票 ====================
    # 中文數字
    def change_num(self):
        self.ensure_one()
        value = int(self.amount_total)

        twdmap = ["零", "壹", "貳", "參", "肆", "伍", "陸", "柒", "捌", "玖"]
        unit = ["元", "拾", "佰", "仟", "萬", "拾", "佰", "仟", "億",
                "拾", "佰", "仟", "萬", "拾", "佰", "仟", "兆"]
        # 冲红负数处理
        xflag = 0
        if value < 0:
            xflag = value
            value = abs(value)
        nums = list(map(int, list(str('%0.2f' % value).replace('.', ''))))
        words = []
        zflag = 0
        start = len(nums) - 3
        for i in range(start, -3, -1):
            if 0 != nums[start - i] or len(words) == 0:
                if zflag:
                    words.append(twdmap[0])
                    zflag = 0
                words.append(twdmap[nums[start - i]])
                words.append(unit[i])
            elif 0 == i or (0 == i % 4 and zflag < 3):
                words.append(unit[i])
                zflag = 0
            else:
                zflag += 1
        words.append("整")
        if xflag < 0:
            words.insert(0, "負")
        return ''.join(words)

    # ========== invoice ==========
    def gw_invoice(self):
        try:
            config = self.env['ir.config_parameter'].sudo()
            gw_seller_department = config.get_param('gateweb_invoice.gw_seller_department')
            # 設定 relate_number
            self.relate_number = self.relate_number or self.env['ir.sequence'].next_by_code('gateweb.invoice')
            # 設定 seller
            # seller = self.company_id
            if not self.seller_identifier:
                raise UserWarning(
                    f'Company:{self.seller_name} -> TaxID:{self.seller_identifier}, need to setup TaxID of company')
            # self.seller_identifier = seller.vat
            # self.seller_name = seller.name
            self.seller_department = gw_seller_department
            # self.seller_address = ('%s%s%s%s' % (
            #     seller.state_id.name if seller.state_id else '',
            #     seller.city if seller.city else '',
            #     seller.street if seller.street else '',
            #     seller.street2 if seller.street2 else '',))
            # 折讓金額
            # self.allowance_amount = self.amount_total
            # 發票類別
            category = self.invoice_category

            line_ids = self.line_ids
            detail = []
            sequence = 0
            for line in line_ids:
                if line.display_type != 'product':
                    continue
                sequence += 1
                detail.append({
                    "amount": line.price_subtotal,
                    "quantity": line.quantity,
                    # "unitPrice": line.price_unit,
                    "unitPrice": line.price_subtotal / (line.quantity if line.quantity else 0),
                    "description": line.product_id.name,
                    "sequenceNumber": '%03d' % sequence,
                    "Remark": ''
                })
            transaction_data_array = {
                "detail": detail,
                "relateNumber": self.relate_number,
                "sellerIdentifier": self.seller_identifier,
                "sellerName": self.seller_name,
                "sellerDepartment": self.seller_department,
                "sellerAddress": self.seller_address,
                "buyerIdentifier": self.buyer_identifier if category == 'B2B' else '0000000000',
                "buyerName": self.buyer_name if category == 'B2B' else '0000000000',
                "buyerEmailAddress": '',
                "invoiceType": self.invoice_type,
                "carrierType": self.carrier_type if self.carrier_type else '',
                "carrierId1": self.carrier_id1 if self.carrier_type else '',
                "carrierId2": self.carrier_id1 if self.carrier_type else '',
                "printMark": self.print_mark,
                "donateMark": self.donate_mark,
                "taxType": self.tax_type,
                "taxRate": 0.05 if self.tax_type == '1' else 0,
                "taxAmount": self.amount_tax,
                "totalAmount": self.amount_total,
                "salesAmount": self.amount_untaxed if self.tax_type == '1' else 0,
                "freeTaxSalesAmount": self.amount_untaxed if self.tax_type == '3' else 0,
                "zeroTaxSalesAmount": self.amount_untaxed if self.tax_type == '2' else 0,
                'customsClearanceMark': '1' if self.tax_type == '2' else '',
            }
            res_config = self.env['res.config.settings'].sudo().search([], limit=1)
            res_config.token()
            response = res_config.invoice(transaction_data_array)
            if response.status_code == 200:
                self.invoice_state = 'uploading'
            else:
                response_data = response.json()
                message = response_data['errors'][0]['errorMessage']
                raise UserError(message)
        except Exception as error:
            raise UserError(error)

    def gw_invoice_status_instantly(self):
        seller_identifier = self.seller_identifier
        relate_number = self.relate_number
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.invoice_status_instantly(seller_identifier, relate_number)
        if response.status_code == 200:
            self.invoice_state = 'invoiced'
            response_data = response.json()
            # self.invoice_no = response_data['migData']['migNumber']
            self.invoice_number = response_data['migData']['migNumber']
            self.gw_invoice_date = response_data['migData']['receiveDate']
            self.invoice_time = response_data['migData']['receiveTime']

    def gw_trash(self):
        transaction_data_array = {
            "relateNumber": self.relate_number,
            "sellerId": self.seller_identifier,
            "cancelReason": self.cancel_reason or 'cancel',
        }
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.trash(transaction_data_array)
        if response.status_code == 200:
            self.invoice_state = 'canceling'
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_trash_status_instantly(self):
        seller_identifier = self.seller_identifier
        relate_number = self.relate_number
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.trash_status_instantly(seller_identifier, relate_number)
        if response.status_code == 200:
            self.invoice_state = 'canceled'
            response_data = response.json()
            self.cancel_date = response_data['migData']['receiveDate']
            self.cancel_time = response_data['migData']['receiveTime']

    # [action] 開立發票
    def action_create_invoice(self):
        if self.invoice_state == 'not invoiced':
            self.gw_invoice()
        self.gw_invoice_status_instantly()

    def action_status_invoice(self):
        if self.invoice_state == 'uploading':
            self.gw_invoice_status_instantly()
        if self.invoice_state == 'canceling':
            self.gw_trash_status_instantly()

    def action_trash_invoice(self):
        return {
            'name': '作廢發票 Invoice Trash',
            'res_model': 'account.move',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('gateweb_invoice.view_gateweb_invoice_trash_form').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def trash_invoice(self):
        if self.invoice_state == 'invoiced':
            self.gw_trash()
        self.gw_trash_status_instantly()

        # ====== 應收憑單取消 ======
        super().button_draft()
        super().button_cancel()

    # def action_allowance(self):
    #     return self.allowance_ids.action_allowance(self.id)

    # ========== allowance ==========

    def gw_allowance(self):
        # 設定 relate_number
        self.allowance_relate_number = self.allowance_relate_number or self.env['ir.sequence'].next_by_code(
            'gateweb.allowance')
        original_relate_number = self.relate_number
        relate_number = self.allowance_relate_number
        # self.original_relate_number = self.original_relate_number or self.invoice_id.relate_number
        seller_id = self.seller_identifier
        tax_type = self.tax_type
        line_ids = self.detail_ids
        detail = []
        sequence = 0
        for line in line_ids:
            sequence += 1
            tax = line.price_total - line.price_subtotal
            detail.append({
                "description": line.name,
                "sequenceNumber": '%03d' % sequence,
                "quantity": line.quantity,
                "unitPrice": line.price_unit,
                "taxType": tax_type,
                "tax": tax,
                "amount": line.price_subtotal,
            })
        transaction_data_array = {
            "detail": detail,
            "originalRelateNumber": original_relate_number,
            "relateNumber": relate_number,
            "sellerId": seller_id,
        }
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance(transaction_data_array)
        if response.status_code == 200:
            # self.state = 'uploading'
            self.invoice_state = 'allowance'
            # response_data = response.json()
            self.allowance_date = datetime.date.today()
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_allowance_status(self):
        original_relate_number = self.relate_number
        relate_number = self.allowance_relate_number
        seller_id = self.seller_identifier
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance_status(seller_id, original_relate_number, relate_number)
        if response.status_code == 200:
            self.invoice_state = 'allowance'
            response_data = response.json()
            self.allowance_date = response_data['migData']['receiveDate']
            self.allowance_time = response_data['migData']['receiveTime']
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_trash_allowance(self):
        original_relate_number = self.relate_number
        relate_number = self.allowance_relate_number
        seller_id = self.seller_identifier
        transaction_data_array = {
            "originalRelateNumber": original_relate_number,
            "relateNumber": relate_number,
            "sellerId": seller_id,
            "cancelReason": self.cancel_reason or 'cancel',
        }
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance_trash(transaction_data_array)
        if response.status_code == 200:
            # self.state = 'canceling'
            self.invoice_state = 'canceled'
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_trash_allowance_status(self):
        original_relate_number = self.relate_number
        relate_number = self.allowance_relate_number
        seller_id = self.seller_identifier
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance_trash_status(seller_id, relate_number)
        if response.status_code == 200:
            self.invoice_state = 'canceled'
            response_data = response.json()
            self.cancel_date = response_data['migData']['receiveDate']
            self.cancel_time = response_data['migData']['receiveTime']

    def action_create_allowance(self):
        if self.invoice_state == 'invoiced':
            self.gw_allowance()

    def action_trash_allowance(self):
        if self.invoice_state == 'allowance':
            self.gw_trash_allowance()
        # self.gw_trash_status()

    # ========== 發送 ==========

    def report_gateweb_invoice(self):
        self.ensure_one()
        for rec in self:
            if rec.invoice_state != 'invoiced':
                return False
            # get pdf
            report_ref = 'gateweb_invoice.action_gateweb_invoices_A4' \
                if rec.invoice_paper == 'A4' else 'gateweb_invoice.action_gateweb_invoices_A5'
            report_data = self.env['ir.actions.report']._render_qweb_pdf(report_ref, rec.id)
            if not report_data:
                return False
            pdf_content = report_data[0]
            ir_values = {
                'datas': base64.b64encode(pdf_content),
                'name': f'{rec.invoice_number}.pdf',
                'store_fname': f'{rec.invoice_number}.pdf',
                'mimetype': 'application/pdf',
                'type': 'binary',
                'res_id': rec.id,
                'res_model': 'account.move',
            }
            domain = [('name', '=', ir_values.get('name'))]
            self.env['ir.attachment'].sudo().search(domain).unlink()
            return self.env['ir.attachment'].sudo().create(ir_values)

    def action_send_and_print(self):
        self.report_gateweb_invoice()
        return super().action_send_and_print()

    # def send_email(self):
    #     self.ensure_one()
    #     # 獲取郵件模板
    #     # email_template = self.env.ref('gateweb_invoice.mail_template_invoice', raise_if_not_found=False)
    #     email_template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
    #     # 如果郵件模板存在，設置附件
    #     if email_template:
    #         # 建立附件
    #         attachment_ids = [(5, 0, 0)]
    #         invoice = self.report_gateweb_invoice()
    #         if invoice:
    #             attachment_ids.append((4, invoice.id))
    #         email_template.attachment_ids = attachment_ids
    #     return email_template
    # def _get_mail_thread_data_attachments(self):
    #     res = super()._get_mail_thread_data_attachments()
    #     # else, attachments with 'res_field' get excluded
    #     return res

    # [action,inherit]
    # def action_send_and_print(self):
    #     record = super(GateWebInvoice, self).action_send_and_print()
    #     template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
    #     if template:
    #         # 建立附件
    #         # attachment_ids = [(5, 0, 0)]
    #         reports = [self.report_gateweb_invoice()]
    #         # 使用 (4, report.id) 附加新附件
    #         attachment_ids = [(4, report.id) for report in reports]
    #         template.attachment_ids = attachment_ids
    #     return record

    # [action,inherit]
    # def action_invoice_sent(self):
    #     self.ensure_one()
    #     # template = self.send_email()
    #     report_action = {
    #         'name': 'Send Invoice',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'account.move.send',
    #         'target': 'new',
    #         'context': {
    #             'active_ids': self.ids,
    #             'default_mail_template_id': template and template.id or False,
    #         },
    #     }
    #     return report_action

    def action_test(self):
        # 使用範例
        encrypter = QRCodeEncrypter()
        try:
            qr_code = encrypter.qr_code_inv(
                invoice_number="AB12345678",
                invoice_date="1120501",
                invoice_time="123456",
                random_number="1234",
                sales_amount=1000,
                tax_amount=50,
                total_amount=1050,
                buyer_identifier="00000000",
                represent_identifier="00000000",
                seller_identifier="12345678",
                business_identifier="12345678",
                product_array=[["product1", "100"], ["product2", "200"]],
                # aes_key="0123456789abcdef0123456789abcdef"
                # aes_key="9A9E4631B46012ED78D86425168855184C9878BDA92F762B23B5F8C48F291BD5"
                aes_key="9A9E4631B46012ED78D8642516885518"
                # aes_key="iFCveb9nGIcl"
            )
            print("QR Code Content:", qr_code)
        except ValueError as e:
            print("Validation Error:", e)

        # for recode in self:
        #     pass


class GateWebAllowance(models.Model):
    _name = 'gateweb.invoice.allowance'
    _description = '折讓單'

    invoice_id = fields.Many2one('account.move', '電子發票')
    detail_ids = fields.One2many('gateweb.invoice.allowance.line', 'allowance_id',
                                 '商品明細', ondelete='cascade')

    # name = fields.Char('折讓單')
    # state = fields.Selection([('not allowance', '未開立'),
    #                           ('uploading', '待上傳'), ('allowance', '已開立'),
    #                           ('canceling', '待作廢'), ('canceled', '已作廢')],
    #                          '狀態', default='not allowance', readonly=True)
    state = fields.Selection([('not allowance', '未開立'), ('allowance', '已開立'), ('canceled', '已作廢')],
                             '狀態', default='not allowance', readonly=True)
    original_relate_number = fields.Char('原始發票唯一號', readonly=True)
    relate_number = fields.Char('折讓單開立唯一號碼', readonly=True)
    seller_id = fields.Char('賣方統編', readonly=True)
    allowance_date = fields.Date('折讓日期', readonly=True)
    allowance_time = fields.Char('折讓時間', readonly=True)
    tax = fields.Integer('稅金', readonly=True)
    amount = fields.Integer('金額', compute='_compute_amount', store=True)

    # ========== 作廢資訊 ==========
    cancel_date = fields.Date('作廢日期', readonly=True)
    # 作廢時間(HH: mm:ss)
    cancel_time = fields.Datetime('作廢時間', readonly=True)
    # 作廢原因
    cancel_reason = fields.Char('作廢原因')

    @api.depends('detail_ids')
    def _compute_amount(self):
        for record in self:
            detail_ids = record.detail_ids

            amount_untaxed = 0
            tax = 0
            amount = 0
            # sequence = 1
            for line in detail_ids:
                tax += line['tax']
                amount += line['amount']
            record.tax = tax
            record.amount = amount
            print(f'==>{tax}/{amount}')

    def gw_allowance(self):
        # 設定 relate_number
        self.relate_number = self.relate_number or self.env['ir.sequence'].next_by_code('gateweb.allowance')
        self.original_relate_number = self.original_relate_number or self.invoice_id.relate_number
        self.seller_id = self.invoice_id.seller_identifier

        line_ids = self.detail_ids
        detail = []
        sequence = 0
        for line in line_ids:
            sequence += 1
            detail.append({
                "description": line.name,
                "sequenceNumber": '%03d' % sequence,
                "quantity": line.quantity,
                "unitPrice": line.unit_price,
                "taxType": line.tax_type,
                "tax": line.tax,
                "amount": line.amount,
            })
        transaction_data_array = {
            "detail": detail,
            "originalRelateNumber": self.original_relate_number,
            "relateNumber": self.relate_number,
            "sellerId": self.seller_id,
        }
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance(transaction_data_array)
        if response.status_code == 200:
            # self.state = 'uploading'
            self.state = 'allowance'
            # response_data = response.json()
            self.allowance_date = datetime.date.today()
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_allowance_status(self):
        seller_id = self.seller_id
        original_relate_number = self.original_relate_number
        relate_number = self.relate_number
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance_status(seller_id, original_relate_number, relate_number)
        if response.status_code == 200:
            self.state = 'allowance'
            response_data = response.json()
            self.allowance_date = response_data['migData']['receiveDate']
            self.allowance_time = response_data['migData']['receiveTime']
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_trash(self):
        transaction_data_array = {
            "originalRelateNumber": self.original_relate_number,
            "relateNumber": self.relate_number,
            "sellerId": self.seller_id,
            "cancelReason": self.cancel_reason or 'cancel',
        }
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance_trash(transaction_data_array)
        if response.status_code == 200:
            # self.state = 'canceling'
            self.state = 'canceled'
        else:
            response_data = response.json()
            message = response_data['errors'][0]['errorMessage']
            raise UserError(message)

    def gw_trash_status(self):
        seller_id = self.seller_id
        relate_number = self.relate_number
        res_config = self.env['res.config.settings'].sudo().search([], limit=1)
        res_config.token()
        response = res_config.allowance_trash_status(seller_id, relate_number)
        if response.status_code == 200:
            self.state = 'canceled'
            response_data = response.json()
            self.cancel_date = response_data['migData']['receiveDate']
            self.cancel_time = response_data['migData']['receiveTime']

    def create_allowance(self):
        if self.state == 'not allowance':
            self.gw_allowance()
        # self.gw_allowance_status()

    def trash_allowance(self):
        if self.state == 'allowance':
            self.gw_trash()
        # self.gw_trash_status()

    def action_allowance(self, invoice_id):
        return {
            'name': '開立折讓 Allowance',
            'res_model': 'gateweb.invoice.allowance',
            'view_mode': 'form',
            'view_id': self.env.ref('gateweb_invoice.view_gateweb_invoice_allowance_form').id,
            'context': {
                'default_invoice_id': invoice_id,
                'active_model': 'gateweb.invoice.allowance',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.model_create_multi
    def create(self, vals_list):
        allowance = super(GateWebAllowance, self).create(vals_list)
        allowance.create_allowance()
        return allowance

    def action_print_allowance(self):
        return self.env.ref('gateweb_invoice.action_gateweb_invoices_allowance').report_action(self)


class GateWebAllowanceLine(models.Model):
    _name = "gateweb.invoice.allowance.line"

    allowance_id = fields.Many2one('gateweb.invoice.allowance', '折讓單號')

    # description
    name = fields.Char('折讓商品', required=True)
    sequence_number = fields.Integer('排列序號', default=1, readonly=True)
    unit_price = fields.Integer('單價', default=0, required=True)
    quantity = fields.Integer('數量', default=1, required=True)
    # unit = fields.Char('單位')
    # 1=taxable應稅,2=zero tax rate零稅率, 3=tax-exempt免稅,4=special tax特種稅,9=compound duties混合稅
    tax_type = fields.Selection([('1', '應稅'), ('2', '零稅率'), ('3', '免稅'), ('4', '特種稅'),
                                 ('9', '混合稅')],
                                '稅別', default='1', required=True)
    tax = fields.Integer('折讓稅額', required=True)
    amount = fields.Integer('折讓金額', default=0, readonly=True,
                            compute='_compute_amount', store=True)

    @api.onchange('unit_price', 'quantity', 'tax_type')
    def _onchange_tax(self):
        unit_price = self.unit_price
        quantity = self.quantity
        tax_type = self.tax_type
        tax_rate = (0.05 if tax_type == '1' or tax_type == '4' or tax_type == '9' else 0)
        self.tax = unit_price * quantity * tax_rate

    @api.depends('unit_price', 'quantity', 'tax')
    def _compute_amount(self):
        for record in self:
            unit_price = record.unit_price
            quantity = record.quantity
            # record.tax = record.tax
            record.amount = unit_price * quantity
