from odoo import fields, models, api
from odoo.exceptions import UserError


class GateWebInvoice(models.Model):
    _inherit = 'account.move'
    # _name = 'gateweb.invoice'
    _description = '關網電子發票'

    allowance_ids = fields.One2many('gateweb.invoice.allowance', 'invoice_id',
                                    '折讓單', ondelete='cascade')
    # ========== 自定義 custom ==========
    invoice_category = fields.Selection([('B2B', 'B2B'), ('B2C', 'B2C')],
                                        '發票類別', default='B2B', required=True)
    invoice_state = fields.Selection([('not invoiced', '未開發票'), ('invoiced', '開立發票'), ('cancelled', '已作廢')],
                                     '電子發票狀態', default='not invoiced', readonly=True)
    allowance_amount = fields.Monetary('剩餘可折讓金額', readonly=True)

    @api.onchange('allowance_ids')
    def onchange_allowance(self):
        records = self.allowance_ids
        amount_total = self.amount_total
        amount = 0
        for line in records:
            amount += line.amount if line.state != 'cancelled' else 0
        if amount_total < amount:
            raise UserError('折讓金額已超出')
        self.allowance_amount = amount_total - amount

    # ========== invoice ==========
    # 待回傳後, 再行增添
    # invoice_no
    invoice_number = fields.Char('發票號碼', readonly=True)
    gw_invoice_date = fields.Date('發票開立日期', readonly=True)
    invoice_time = fields.Datetime('發票開立時間', readonly=True)

    # 開立發票
    def _invoice(self):
        # self.invoice_date = fields.Date.today()
        # self.invoice_time = datetime.time
        self.relate_number = self.env['ir.sequence'].next_by_code('gateweb.invoice')

    # ========== 賣方資訊 ==========
    seller_identifier = fields.Char('賣方統編', compute='compute_seller', store=True)
    # 必須為繁體中文（財政部登記姓名一致）
    seller_name = fields.Char('賣方公司名稱')
    # 該欄位值由關網提供＆若為子母公司設定，依照不同公司之印表機名稱代入
    seller_department = fields.Char('印表機名稱')
    # 必須為繁體中文（財政部登記一致）
    seller_address = fields.Char('賣方營業登記地址')

    # seller_person_incharge = fields.Char('賣方負責人')
    # seller_telephone_number = fields.Char('賣方電話')
    # seller_facsimile_number = fields.Char('賣方傳真')
    # seller_email_address  = fields.Char('賣方電子郵件地址')
    # seller_customer_number = fields.Char('賣方號碼')
    # seller_role_remark = fields.Char('發票總備註')

    def compute_seller(self):
        self.seller_identifier = self.company_id.vat if self.company_id else False
        self.seller_name = self.company_id.name if self.company_id else False
        self.seller_department = self.company_id.address if self.company_id else False
        self.seller_address = self.company_id.address if self.company_id else False

    # ========== 買方資訊 ==========
    # 非營業人固定放0000000000
    buyer_identifier = fields.Char('買方統一編號')
    # 非營業人固定放0000000000
    buyer_name = fields.Char('買方公司名稱')
    # buyer_address = fields.Char('買方營業地址')
    # buyer_person_incharge = fields.Char('買方負責人')
    # buyer_telephone_number = fields.Char('買方電話')
    # buyer_facsimile_number = fields.Char('買方傳真')
    # B2B，若需要發送E-Mail PDF檔，將買方信箱郵件地址放上
    buyer_email_address = fields.Char('買方電子郵件地址')
    # buyer_customer_number = fields.Char('買方號碼')
    # 若有值顯示於發票備註欄位
    # buyer_role_remark = fields.Char('發票總備註')
    # 待回傳後, 再行增添
    # 作廢日期(YYYYMMDD)

    # 未填值則由關網自動產生填入
    # random_number = fields.Char('發票防偽隨機碼')
    # 必須是一組唯一的編號，可以是內部訂單號碼或自訂規則之編碼，未來查詢發票及異動對應使用
    # 在此與 sale_order name 同名
    relate_number = fields.Char('發票唯一號碼')
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
                                  '索取紙本發票', default='Y')
    donate_mark = fields.Selection([('1', '是'), ('0', '否')],
                                   '捐贈發票', default='0')
    # 受贈單位代碼donateMark is 1 , npoban 必填3-7碼數字
    npo_ban = fields.Char("捐贈碼")

    # ========== 金額資訊(稅額) ==========
    sales_amount = fields.Integer('銷售額(應稅)', default=0)
    free_tax_sales_amount = fields.Integer('銷售額(免稅)', default=0)
    zero_tax_sales_amount = fields.Integer('銷售額(零稅率)', default=0)
    tax_type = fields.Selection([('1', '應稅'), ('2', '免稅'),
                                 ('3', '零稅率')],
                                '課稅別', default='1')
    # tax Type(1)=0.05、tax Type(2、3)= 0 、tax Type=(3) CustomsClearanceMark必填
    tax_rate = fields.Float('稅率', default=0)
    # 1: 非經海關出口   2:經海關出口
    customs_clearance_mark = fields.Selection([('1', '非經海關出口'), ('2', '經海關出口')],
                                              '零稅率通關方式', default='1')

    @api.onchange('amount_tax', 'amount_total')
    def _onchange_sales_amount(self):
        amount_tax = self.amount_tax
        amount_total = self.amount_total
        amount = amount_total - amount_tax

        # 稅率
        self.tax_type = '1' if amount_tax > 0 else '2'
        self.tax_rate = 0.05
        # 銷售金額
        self.sales_amount = amount if self.tax_type == '1' else 0
        self.free_tax_sales_amount = amount if self.tax_type == '2' else 0
        # self.zero_tax_sales_amount = amount if tax_type == 3 else 0
        self.zero_tax_sales_amount = 0

    # amount_tax
    # tax_amount = fields.Integer('營業稅額')

    # totalAmount = salesAmount + free_tax_sales_amount + zero_tax_sales_amount + tax_amount
    # amount_total
    # total_amount = fields.Integer('總計金額')

    # ========== 作廢資訊 ==========
    cancel_date = fields.Date('作廢日期', readonly=True)
    # 作廢時間(HH: mm:ss)
    cancel_time = fields.Datetime('作廢時間', readonly=True)
    # 作廢原因
    cancel_reason = fields.Char('作廢原因')

    # 作廢
    def _cancel(self):
        cancel_reason = self.cancel_reason
        if not cancel_reason:
            raise UserError('作廢原因,尚未填寫')
        # self.cancel_date = fields.Date.today()
        # self.cancel_time = fields.Datetime.now()

    # ========== Account Move ==========
    def create_invoice(self):
        pass


class GateWebAllowance(models.Model):
    _name = "gateweb.invoice.allowance"
    _description = '折讓單'

    invoice_id = fields.Many2one('account.move', '電子發票')
    detail_ids = fields.One2many('gateweb.invoice.allowance.line', 'allowance_id',
                                 '商品明細', ondelete='cascade')

    # name = fields.Char('折讓單')
    state = fields.Selection([('not allowance', '未開立'), ('allowance', '已開立'), ('cancelled', '已作廢')],
                             '狀態', default='not allowance', readonly=True)

    original_relate_number = fields.Char('原始發票唯一號', readonly=True)
    relate_number = fields.Char('折讓單開立唯一號碼', readonly=True)
    seller_id = fields.Char('賣方統編', required=True)
    allowance_date = fields.Date('折讓日期', readonly=True)

    amount = fields.Integer('金額', readonly=True)

    @api.onchange('detail_ids')
    def onchange_detail_ids(self):
        detail_ids = self.detail_ids
        amount = 0
        sequence = 1
        for line in detail_ids:
            line['sequence_number'] = (sequence or line['sequence_number'])
            sequence += 1
            amount += line['amount']
        self.amount = amount

    # 折讓
    def _allowance(self):
        # self.allowance_date = fields.Date.today()
        self.relate_number = self.env['ir.sequence'].next_by_code('gateweb.allowance')

    # ========== 作廢資訊 ==========
    cancel_date = fields.Date('作廢日期', readonly=True)
    # 作廢時間(HH: mm:ss)
    cancel_time = fields.Datetime('作廢時間', readonly=True)
    # 作廢原因
    cancel_reason = fields.Char('作廢原因')

    # 作廢
    def _cancel(self):
        cancel_reason = self.cancel_reason
        if not cancel_reason:
            raise UserError('作廢原因,尚未填寫')
        # self.cancel_date = fields.Date.today()
        # self.cancel_time = fields.Datetime.now()


class GateWebAllowanceLine(models.Model):
    _name = "gateweb.invoice.allowance.line"

    allowance_id = fields.Many2one('gateweb.invoice.allowance', '折讓單號')

    # description
    name = fields.Char('折讓商品', required=True)
    sequence_number = fields.Integer('排列序號', default=1, readonly=True)
    unit_price = fields.Integer('單價', required=True)
    quantity = fields.Integer('數量', default=1, required=True)
    # unit = fields.Char('單位')
    # 1=taxable應稅,2=zero tax rate零稅率, 3=tax-exempt免稅,4=special tax特種稅,9=compound duties混合稅
    tax_type = fields.Selection([('1', '應稅'), ('2', '零稅率'), ('3', '免稅'), ('4', '特種稅'),
                                 ('9', '混合稅')],
                                '稅別', default='1', required=True)
    tax = fields.Integer('折讓稅額', default=0, required=True)
    amount = fields.Integer('折讓金額', default=0, required=True)
