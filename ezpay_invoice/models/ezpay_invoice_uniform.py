# -*- coding: utf-8 -*-

import random
import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from .ezpay_decrypt import *
import datetime
from json import loads
# from num2chinese import num2chinese


tax_sign = {
    '1': 'TX',
    '2': 'ZX',
    '3': ''
}


class EzpayInvoiceUniform(models.Model):
    _name = 'ezpay.invoice.uniform'

    name = fields.Char(string='統一發票號碼')
    IIS_Award_Flag = fields.Selection(string='中獎旗標', selection=[('0', '未中獎'), ('1', '已中獎'), ('X', '有統編之發票')])
    IIS_Award_Type = fields.Selection(string='中獎種類', selection=[('0', '未中獎'), ('6', '六獎 二百元'), ('5', '五獎 一千元'),
                                                                ('4', '四獎 四千元'), ('3', '三獎 一萬元'), ('2', '二獎 四萬元'),
                                                                ('1', '頭獎 二十萬元'), ('7', '特獎 二百萬元'), ('8', '特別獎 一千萬'),
                                                                ('9', '無實體2000元獎'), ('10', '無實體百萬元獎')])
    IIS_Carruer_Num = fields.Char(string='載具編號')
    IIS_Carruer_Type = fields.Selection(string='載具類別', selection=[('0', '手機條碼載具'), ('1', '自然人憑證條碼載具'),
                                                                  ('2', 'ezPay 電子發票載具')])
    IIS_Category = fields.Selection(string='發票類別', selection=[('B2B', '有統編'), ('B2C', '無統編')])
    IIS_Check_Number = fields.Char(string='發票檢查碼')
    IIS_Clearance_Mark = fields.Selection(string='通關方式', selection=[('1', '經海關出口'), ('2', '非經海關出口')])
    IIS_Create_Date = fields.Datetime(string='發票開立時間')
    IIS_Customer_Addr = fields.Char(string='客戶地址')
    IIS_Customer_Email = fields.Char(string='客戶電子信箱')
    IIS_Customer_ID = fields.Char(string='客戶編號')
    IIS_Customer_Name = fields.Char(string='客戶名稱')
    IIS_Customer_Phone = fields.Char(string='客戶電話')
    IIS_Identifier = fields.Char(string='買方統編')
    IIS_Invalid_Status = fields.Selection(string='發票作廢狀態', selection=[('1', '已作廢'), ('0', '未作廢')], default='0')
    IIS_IP = fields.Char(string='發票開立IP')
    IIS_Issue_Status = fields.Selection(string='發票開立狀態', selection=[('1', '發票開立'), ('0', '發票註銷')], default='1')
    IIS_Love_Code = fields.Char(string='捐款單位捐贈碼')
    IIS_Mer_ID = fields.Char(string='合作特店編號')
    IIS_Number = fields.Char(string='發票號碼')
    IIS_Print_Flag = fields.Selection(string='列印旗標', selection=[('1', '列印'), ('0', '不列印')])
    IIS_Random_Number = fields.Char(string='隨機碼')
    IIS_Relate_Number = fields.Char(string='合作特店自訂編號')
    IIS_Remain_Allowance_Amt = fields.Char(string='剩餘可折讓金額')
    IIS_Sales_Amount = fields.Char(string='發票金額')
    IIS_Sales_Amt = fields.Char(string='未稅金額')
    IIS_Tax_Amount = fields.Char(string='稅金')
    IIS_Tax_Rate = fields.Char(string='稅率')
    IIS_Tax_Type = fields.Selection(string='課稅別', selection=[('1', '應稅'), ('2', '零稅率'), ('3', '免稅'), ('9', '混合應稅與免稅')])
    IIS_Turnkey_Status = fields.Selection(string='發票上傳後接收狀態', selection=[('C', '成功'), ('E', '失敗'), ('G', '處理中')])
    IIS_Type = fields.Selection(string='發票種類', selection=[('07', '一般稅額計算'), ('08', '特種稅額計算')])
    IIS_Upload_Date = fields.Datetime(string='發票上傳時間')
    IIS_Upload_Status = fields.Selection(string='發票上傳狀態', selection=[('1', '已上傳'), ('0', '未上傳')])
    InvoiceRemark = fields.Char(string='發票備註')
    ItemAmount = fields.Char(string='商品合計')
    ItemCount = fields.Char(string='商品數量')
    ItemName = fields.Char(string='商品名稱')
    ItemPrice = fields.Char(string='商品價格')
    ItemRemark = fields.Char(string='商品備註說明')
    ItemTaxType = fields.Char(string='商品課稅別')
    ItemUnit = fields.Char(string='商品單位')
    PosBarCode = fields.Char(string='顯示電子發票BARCODE用')
    QRCode_Left = fields.Char(string='顯示電子發票QRCODE左邊用')
    QRCode_Right = fields.Char(string='顯示電子發票QRCODE右邊用')
    related_number = fields.Char(string='發票開立序號')
    RtnCode = fields.Char(string='回應代碼')
    RtnMsg = fields.Char(string='回應訊息')
    CheckMacValue = fields.Char(string='檢查碼')

    invoice_month = fields.Char(string='發票月份')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False)

    # Odoo都是使用GMT標準時間來儲存
    # def trasfer_time(self, time_before):
    #     # time_after = (datetime.datetime.strptime(time_before, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    #     time_after = datetime.datetime.strptime(time_before, '%Y-%m-%d %H:%M:%S')
    #     return time_after
    def split_order_line(self):
        self.ensure_one()

        lines = []
        ItemAmount = list(self.ItemAmount.split('|'))
        ItemCount = list(self.ItemCount.split('|'))
        ItemName = list(self.ItemName.split('|'))
        ItemPrice = list(self.ItemPrice.split('|'))
        ItemRemark = list(self.ItemRemark.split('|'))
        ItemTaxType = list(self.ItemTaxType.split('|'))
        ItemUnit = list(self.ItemUnit.split('|'))
        for item in list(zip(ItemAmount, ItemCount, ItemName, ItemPrice, ItemTaxType, ItemUnit)):
            line = {
                'ItemAmount': int(float(item[0])),
                'ItemCount': item[1],
                'ItemName': item[2],
                'ItemPrice': int(float(item[3])),
                # 'ItemRemark': item[4],
                'ItemTaxSign': tax_sign.get(item[4]),
                'ItemUnit': item[5],
            }
            lines.append(line)
        return lines

    def count_order_line(self):
        self.ensure_one()

        return len(self.ItemAmount.split('|'))

    def change_num(self):
        self.ensure_one()
        value = int(self.IIS_Sales_Amount)

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

    def invalid_invoice(self):

        invoice = EzpayInvoiceinvalid()

        #作業ezpay 電子發票
        company_id = self.env.company

        # 判斷設定是否為測試電子發票模式
        ezpay_demo_mode = company_id.ezpay_demo_mode
        if ezpay_demo_mode:
            url = 'https://cinv.ezpay.com.tw/Api/invoice_invalid'
        else:
            url = 'https://inv.ezpay.com.tw/Api/invoice_invalid'

        # ezpay_invoice.Invoice_Method = method
        invoice.Invoice_Url = url
        # TODO 檢查以下三個參數，缺少任一個就跳出警告
        # if not company_id.ezpay_MerchantID or \
        #         not company_id.ezpay_HashKey or not company_id.ezpay_HashIV:
        #     raise UserError('ezpay電子發票連線設定不完整')
        config = self.env['res.config.settings'].get_values()
        if not config:
            raise UserError('ezpay電子發票連線設定不完整')
        ezpay_MerchantID = config['ezpay_MerchantID']
        ezpay_HashKey = config['ezpay_HashKey']
        ezpay_HashIV = config['ezpay_HashIV']
        invoice.MerchantID = ezpay_MerchantID
        invoice.HashKey = ezpay_HashKey
        invoice.HashIV = ezpay_HashIV

        invoice.Send['InvoiceNumber'] = self.IIS_Number
        invoice.Send['InvalidReason'] = "測試作廢"

        aReturn_Info = invoice.do_invalid()
        aReturn_Info = loads(aReturn_Info.content)
        if aReturn_Info['Status'] != 'SUCCESS':
            raise UserError('串接電子發票失敗!!錯誤訊息：' + aReturn_Info['Status'] + aReturn_Info['Message'])
        else:
            self.update({
                'IIS_Invalid_Status': '1',
            })
            self.env['account.move'].sudo().search([('ezpay_invoice_id', '=', self.id)]).write({'uniform_state': 'invalid'})
            # raise UserError('電子發票作廢成功：' + aReturn_Info['Status'] + aReturn_Info['Message'])