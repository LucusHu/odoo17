# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from .ezpay_decrypt import *
import datetime
from json import loads


# 會計(account move)
class EZPAYINVOICEInherit(models.Model):
    _inherit = "account.move"

    ezpay_invoice_id = fields.Many2one('ezpay.invoice.uniform', string='統一發票號碼', readonly=True)

    uniform_state = fields.Selection(
        selection=[('to invoice', '未開電子發票'), ('invoiced', '已開電子發票'), ('invalid', '已作廢')],
        string='電子發票狀態',
        default='to invoice', readonly=True)
    ezpay_tax_type = fields.Selection(selection=[('1', '含稅'), ('0', '未稅')], string='商品單價是否含稅', default='1',
                                      readonly=True, states={'draft': [('readonly', False)]})

    show_create_invoice = fields.Boolean(string='控制是否顯示串接電子發票', compute='get_access_invoice_mode')
    show_hand_in_field = fields.Boolean(string='控制是否顯示手動填入的選項', compute='get_access_invoice_mode')

    is_donation = fields.Boolean(string='是否捐贈發票')
    is_print = fields.Boolean(string='是否索取紙本發票')

    carruerType = fields.Selection(
        selection=[('0', '手機條碼載具'), ('1', '自然人憑證條碼載具'), ('2', 'ezPay 電子發票載具')],
        string='載具類別')
    categoryType = fields.Selection(selection=[('B2B', 'B2B'), ('B2C', 'B2C')],
                                    string='發票類別', default='B2B')
    lovecode = fields.Char(string='捐贈碼')
    carruernum = fields.Char(string='載具號碼')
    ezpay_CustomerIdentifier = fields.Char(string='統一編號')
    ez_print_address = fields.Char(string='發票寄送地址')
    ez_ident_name = fields.Char(string='發票抬頭')

    is_refund = fields.Boolean(string='是否為折讓', readonly=True)
    refund_finish = fields.Boolean(string='折讓完成', readonly=True)

    IA_Allow_No = fields.Char(string='折讓單號', readonly=True)
    IA_Invoice_No = fields.Many2one('ezpay.invoice.uniform', string='要折讓的發票', readonly=True)

    III_Invoice_No = fields.Many2one('ezpay.invoice.uniform', string='要作廢的發票', readonly=True)

    IIS_Remain_Allowance_Amt = fields.Char(string='剩餘可折讓金額', related='ezpay_invoice_id.IIS_Remain_Allowance_Amt')
    IIS_Sales_Amount = fields.Char(string='發票金額', related='ezpay_invoice_id.IIS_Sales_Amount')
    IIS_Invalid_Status = fields.Selection(related='ezpay_invoice_id.IIS_Invalid_Status')
    IIS_Issue_Status = fields.Selection(related='ezpay_invoice_id.IIS_Issue_Status')
    IIS_Relate_Number = fields.Char(related='ezpay_invoice_id.IIS_Relate_Number')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.ezpay_CustomerIdentifier = self.partner_id.vat
            self.ez_print_address = "%s%s%s" % (
            self.partner_id.state_id.name, self.partner_id.city_id.name, self.partner_id.street)

            if self.partner_id.is_company:
                self.ez_ident_name = self.partner_id.mfp_invoice if self.partner_id.mfp_invoice else self.partner_id.name
            else:
                self.ez_ident_name = self.partner_id.partner_id.mfp_invoice if self.partner_id.partner_id.mfp_invoice else self.partner_id.parent_id.name

    @api.onchange('is_print', 'carruerType')
    def set_carruerType_false(self):
        if self.is_print is True and self.carruerType is not False:
            self.carruerType = False
            self.carruernum = False

    @api.onchange('is_donation')
    def set_is_print_false(self):
        if self.is_donation is True:
            self.is_print = False

    # 控制是否顯示手動開立的按鈕
    @api.depends('ezpay_invoice_id', 'IA_Invoice_No', 'III_Invoice_No')
    def get_access_invoice_mode(self):
        for row in self:
            auto_invoice_mode = row.company_id.auto_invoice
            if auto_invoice_mode == 'automatic':
                row.show_create_invoice = False
            elif auto_invoice_mode == 'hand in':
                row.show_hand_in_field = True
            else:
                row.show_create_invoice = True
                row.show_hand_in_field = False

    # 當開立模式是自動開立時，在應收憑單進行過帳時，同時進行開立發票的動作。
    def action_post(self):
        res = super(EZPAYINVOICEInherit, self).action_post()
        for row in self:
            auto_invoice = row.company_id.auto_invoice
            # auto_send_invoice = row.partner_id.is_auto_send
            # 如果為折讓單，則不自動產生電子發票
            if auto_invoice == 'automatic' and row.move_type == 'out_invoice':
                row.create_ezpay_invoice()
                # if auto_send_invoice:
                row.send_ezpay_invoice()
            # if auto_invoice == 'automatic' and row.move_type == 'out_refund':
            #     row.run_refund()

        return res

    def send_ezpay_invoice(self):
        invoice_report_id = self.env.ref('ezpay_invoice.action_print_ezpay_invoice')
        generated_report = invoice_report_id._render_qweb_pdf(self.id)
        data_record = base64.b64encode(generated_report[0])
        ir_values = {
            'name': 'Ezpay Invoice',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'account.move',
        }
        report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        email_template = self.env.ref('account.email_template_edi_invoice')
        if email_template:
            email_values = {
                'email_to': self.partner_id.email,
                # 'email_from': self.env.user.email,
            }
            email_template.attachment_ids = [(4, report_attachment.id)]
            email_template.send_mail(self.id, email_values=email_values,
                                     force_send=True)
            email_template.attachment_ids = [(5, 0, 0)]

    @api.model
    def ezpay_invoice_init(self, ezpay_invoice, type, method, company_id=False):

        company_id = company_id or self.env.company

        # 判斷設定是否為測試電子發票模式
        ezpay_demo_mode = company_id.ezpay_demo_mode
        if ezpay_demo_mode:
            url = 'https://cinv.ezpay.com.tw/Api/invoice_issue'
            # url = 'https://cinv.ezpay.com.tw/Api/crossBorderInvoiceIssue'
        else:
            url = 'https://inv.ezpay.com.tw/Api/invoice_issue'
            # url = 'https://cinv.ezpay.com.tw/Api/crossBorderInvoiceIssue'

        # ezpay_invoice.Invoice_Method = method
        ezpay_invoice.Invoice_Url = url
        # TODO 檢查以下三個參數，缺少任一個就跳出警告
        config = self.env['res.config.settings'].get_values()
        if not config:
            raise UserError('ezpay電子發票連線設定不完整')
        ezpay_MerchantID = config['ezpay_MerchantID']
        ezpay_HashKey = config['ezpay_HashKey']
        ezpay_HashIV = config['ezpay_HashIV']
        # if not company_id.ezpay_MerchantID or \
        #         not company_id.ezpay_HashKey or not company_id.ezpay_HashIV:
        #     raise UserError('ezpay電子發票連線設定不完整')
        if not ezpay_MerchantID or \
                not ezpay_HashKey or not ezpay_HashIV:
            raise UserError('ezpay電子發票連線設定不完整')
        ezpay_invoice.MerchantID = ezpay_MerchantID
        ezpay_invoice.HashKey = ezpay_HashKey
        ezpay_invoice.HashIV = ezpay_HashIV

    # 匯入Odoo發票明細到電子發票中
    def prepare_item_list(self):
        self.ensure_one()

        res = []
        amount_total = 0.0
        for line in self.invoice_line_ids:
            taxable = line.tax_ids.filtered(lambda t: t.amount >= 5.0)
            ItemPrice = float_round(line.price_total / int(line.quantity), precision_digits=2)
            # ItemPrice = line.price_unit
            # if not res:
            res.append({
                'ItemName': line.product_id.name[:30],
                'ItemCount': int(line.quantity),
                'ItemUnit': line.product_uom_id.name[:6],
                'ItemPrice': ItemPrice,
                'ItemTaxType': '1' if len(taxable.ids) >= 1 else '3',
                'ItemAmt': float_round(ItemPrice * int(line.quantity), precision_digits=2),
                'Comment': line.name[:40]
            })
            amount_total += line.price_total
        return res, amount_total

    # 準備客戶基本資料
    @api.model
    def prepare_customer_info(self, ezpay_invoice):
        # ezpay_invoice.Send['CustomerID'] = ''
        # 新版統編寫法，取得電商前端統編
        ezpay_invoice.Send[
            'CustomerIdentifier'] = self.ezpay_CustomerIdentifier if self.ezpay_CustomerIdentifier else self.partner_id.vat

        ezpay_invoice.Send['MerchantOrderNo'] = self.name.replace('/', '')
        # 新版抬頭寫法，取得電商抬頭，如果沒有預設取得partner 名稱
        ezpay_invoice.Send['BuyerName'] = self.ez_ident_name if self.ez_ident_name else self.partner_id.name

        # 新版寄送地址寫法，取得電商發票寄送地址，如果沒有預設取得partner 地址
        addr = "%s%s%s" % (self.partner_id.state_id.name, self.partner_id.city_id.name, self.partner_id.street)
        # ezpay_invoice.Send['BuyerAddress'] = self.ez_print_address if self.ez_print_address else addr
        # ezpay_invoice.Send['BuyerPhone'] = self.partner_id.mobile if self.partner_id.mobile else ''
        ezpay_invoice.Send['BuyerAddress'] = ''
        ezpay_invoice.Send['BuyerPhone'] = ''
        # ezpay_invoice.Send['BuyerEmail'] = self.partner_id.email if self.partner_id.email else ''
        # ezpay_invoice.Send['ClearanceMark'] = ''
        ezpay_invoice.Send['Category'] = self.categoryType
        ezpay_invoice.Send['PrintFlag'] = 'Y'
        if self.categoryType == 'B2B':
            ezpay_invoice.Send[
                'BuyerUBN'] = self.ezpay_CustomerIdentifier if self.ezpay_CustomerIdentifier else '00000000'
            ezpay_invoice.Send['PrintFlag'] = 'Y'
        ezpay_invoice.Send['TaxType'] = '1'
        ezpay_invoice.Send['TaxRate'] = '5'

    # 檢查發票邏輯
    def validate_ezpay_invoice(self):
        self.ensure_one()

        if self.is_print is True and self.is_donation is True:
            raise UserError('列印發票與捐贈發票不能同時勾選！！')
        elif self.is_print is True and self.carruerType is not False:
            raise UserError('列印發票時，不能夠選擇發票載具！！')
        elif self.is_print is False and self.carruerType in ['0', '1'] and self.is_donation is False:
            if self.carruernum is False:
                raise UserError('請輸入發票載具號碼！！')

        if self.is_donation is True and self.lovecode is not False:
            if not self.check_lovecode(self.lovecode):
                raise UserError('愛心碼不存在！！')

        # 檢查客戶地址
        # if self.ez_print_address is False and self.partner_id.street is False:
        #     raise UserError('請到客戶資料中輸入客戶地址或在當前頁面輸入發票寄送地址！')

    # 產生電子發票
    def create_ezpay_invoice(self):
        self.ensure_one()
        if self.move_type != 'out_invoice':
            raise UserError('產生電子發票的應收憑單類型應該為客戶應收憑單')
        if self.ezpay_invoice_id:
            raise UserError('己開立過電子發票，需將本筆取消')
        self.validate_ezpay_invoice()

        invoice = EzpayInvoice()
        company_id = self.company_id
        self.ezpay_invoice_init(invoice, 'Invoice/Issue', 'INVOICE', company_id)
        for line in self.invoice_line_ids:
            taxable = line.tax_ids.filtered(lambda t: t.amount >= 5.0)
            ItemPrice = float_round(line.price_total / int(line.quantity), precision_digits=2)
            # ItemPrice = line.price_unit
            if invoice.Send['ItemName'] == '':
                invoice.Send['ItemName'] = line.product_id.name[:30]
                invoice.Send['ItemCount'] = str(int(line.quantity))
                invoice.Send['ItemUnit'] = line.product_uom_id.name[:6]
                invoice.Send['ItemPrice'] = str(ItemPrice)
                invoice.Send['ItemTaxType'] = '1' if len(taxable.ids) >= 1 else '3'
                invoice.Send['ItemAmt'] = str(float_round(ItemPrice * int(line.quantity), precision_digits=2))
                invoice.Send['Comment'] = ''
            else:
                invoice.Send['ItemName'] += '|' + line.product_id.name[:30]
                invoice.Send['ItemCount'] += str('|' + str(int(line.quantity)))
                invoice.Send['ItemUnit'] += '|' + line.product_uom_id.name[:6]
                invoice.Send['ItemPrice'] += '|' + str(ItemPrice)
                invoice.Send['ItemTaxType'] += '|1' if len(taxable.ids) >= 1 else '|3'
                invoice.Send['ItemAmt'] += '|' + str(float_round(ItemPrice * int(line.quantity), precision_digits=2))
                invoice.Send['Comment'] += ''
        invoice.Send['TotalAmt'] = int(self.amount_total)
        invoice.Send['OriginalCurrencyAmount'] = int(self.amount_total)
        invoice.Send['Amt'] = int(self.amount_untaxed)  # 未稅
        invoice.Send['TaxAmt'] = int(self.amount_tax)  # 總稅額
        invoice.Send['TimeStamp'] = int(datetime.datetime.now().timestamp())
        # invoice.Send['IIS_Tax_Amount']

        if self.is_donation is True:
            invoice.Send['Donation'] = '1'
            invoice.Send['LoveCode'] = self.lovecode
        if self.is_print or self.ezpay_CustomerIdentifier:
            invoice.Send['PrintFlag'] = 'Y'
        if self.carruerType is not False:
            invoice.Send['CarrierType'] = self.carruerType
            if self.carruernum is not False and invoice.Send['CarrierType'] in ['0', '1']:
                invoice.Send['CarrierNum'] = self.carruernum

        self.prepare_customer_info(invoice)
        record = self.env['ezpay.invoice.uniform'].create({
            'company_id': self.company_id.id
        })
        # invoice.Send['RelateNumber'] = record.related_number
        aReturn_Info = invoice.Check_Out()
        aReturn_Info = loads(aReturn_Info.content)
        if aReturn_Info['Status'] != 'SUCCESS':
            raise UserError('串接電子發票失敗!!錯誤訊息：' + aReturn_Info['Status'] + aReturn_Info['Message'])
        else:
            result_data = loads(aReturn_Info['Result'])
            record.name = result_data['InvoiceNumber']
            self.ezpay_invoice_id = record
            self.uniform_state = 'invoiced'
            invoice_create = datetime.datetime.strptime(result_data['CreateTime'], '%Y-%m-%d %H:%M:%S')
            datetime_int = int(invoice_create.strftime("%m"))
            date = invoice_create.date()
            if datetime_int == 11 or datetime_int == 12:
                record.invoice_month = str(date.year - 1911) + '年11-12月'
            elif datetime_int % 2 == 0:
                record.invoice_month = str(date.year - 1911) + '年0' + str(
                    datetime_int - 1) + '-' + invoice_create.strftime("%m") + '月'
            elif datetime_int % 2 == 1:
                record.invoice_month = str(date.year - 1911) + '年' + invoice_create.strftime("%m") + '-0' + str(
                    datetime_int + 1) + '月'
            record.update({
                'name': result_data['InvoiceNumber'],
                'IIS_Number': result_data['InvoiceNumber'],
                'IIS_Carruer_Num': invoice.Send['CarrierNum'] if self.carruernum else '',
                'IIS_Carruer_Type': invoice.Send['CarrierType'] if self.carruernum else '',
                'related_number': result_data['InvoiceTransNo'],
                'IIS_Sales_Amount': result_data['TotalAmt'],
                'IIS_Random_Number': result_data['RandomNum'],
                'IIS_Create_Date': result_data['CreateTime'],
                'IIS_Check_Number': result_data['CheckCode'],
                'QRCode_Left': result_data['QRcodeL'],
                'QRCode_Right': result_data['QRcodeR'],
                'IIS_Customer_Name': invoice.Send['BuyerName'],
                'IIS_Customer_Phone': invoice.Send['BuyerPhone'],
                'IIS_Customer_Email': invoice.Send['BuyerEmail'],
                'IIS_Customer_Addr': invoice.Send['BuyerAddress'],
                'IIS_Identifier': invoice.Send['CustomerIdentifier'],
                'RtnCode': aReturn_Info['Status'],
                'RtnMsg': aReturn_Info['Message'],
                'ItemName': invoice.Send['ItemName'],
                'ItemCount': invoice.Send['ItemCount'],
                'ItemUnit': invoice.Send['ItemUnit'],
                'ItemPrice': invoice.Send['ItemPrice'],
                'ItemTaxType': invoice.Send['ItemTaxType'],
                'ItemAmount': invoice.Send['ItemAmt'],
                'ItemRemark': invoice.Send['Comment'],
                'IIS_Tax_Amount': invoice.Send['TaxAmt'],  # 總稅額
                'IIS_Sales_Amt': invoice.Send['Amt'],  # 未稅
            })
