from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'gateweb.invoice'
    _description = 'Description'

    sale_id = fields.Many2one('sale.order', '應收憑單')
    # amount, quantity, unitPrice, description, sequenceNumber
    # price_total, product_uom_qty, price_unit, name, sequence
    detail_ids = fields.One2many(related='sale_id.order_line')

    invoice_category = fields.Selection([('B2B', 'B2B'), ('B2C', 'B2C')],
                                        '發票類別', default='B2B')
    # 待回傳後, 再行增添
    invoice_number = fields.Char('發票號碼', readonly=True)
    invoice_date = fields.Date('發票開立日期', readonly=True)
    invoice_time = fields.Datetime('發票開立時間', readonly=True)

    seller_identifier = fields.Char('賣方統編')
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

    # 非營業人固定放0000000000
    buyer_identifier = fields.Char('買方統一編號')
    # 非營業人固定放0000000000
    buyer_name = fields.Char('買方公司名稱')
    # buyer_address = fields.Char('買方營業地址')
    # buyer_person_incharge = fields.Char('買方負責人')
    # buyer_telephone_number = fields.Char('買方電話')
    # buyer_facsimile_number = fields.Char('買方傳真')
    # buyer_email_address = fields.Char('買方電子郵件地址')
    # buyer_customer_number = fields.Char('買方號碼')
    # 若有值顯示於發票備註欄位
    # buyer_role_remark = fields.Char('發票總備註')

    # is_print = fields.Boolean('列印')
    # is_donate = fields.Boolean('捐贈')
    # donate_number = fields.Char('愛心碼')
    # print_address = fields.Char('發票寄送地址')
    # ident_name = fields.Char('發票抬頭')
    # ident = fields.Char('統一編號')

    # 未填值則由關網自動產生填入
    # random_number = fields.Char('發票防偽隨機碼')
    # 必須是一組唯一的編號，可以是內部訂單號碼或自訂規則之編碼，未來查詢發票及異動對應使用
    # 在此與 sale_order name 同名
    relate_number = fields.Char('相關號碼')
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
    carrier_id1 = fields.Char('載具顯碼')
    carrier_id2 = fields.Char('載具隱碼')
    # carruer_number = fields.Char('載具號碼')
    # 1: 非經海關出口   2:經海關出口
    # customs_clearance_mark = fields.Selection([('1', '非經海關出口'), ('2', '經海關出口')],
    #                                           '零稅率通關方式',
    #                                           default='1')
    print_mark = fields.Selection([('Y', '是'), ('N', '否')],
                                  '索取紙本發票', default='Y')
    donate_mark = fields.Selection([('Y', '是'), ('N', '否')],
                                   '捐贈發票', default='N')
    sales_amount = fields.Char('銷售額(應稅)')
    free_tax_sales_amount = fields.Char('銷售額(免稅)')
    zero_tax_sales_amount = fields.Char('銷售額(零稅率)')
    tax_type = fields.Selection([('1', '0.05'), ('2', '0.00'),
                                 ('3', '0.00')],
                                '課稅別')
    # tax Type(1)=0.05、tax Type(2、3)= 0 、tax Type=(3) CustomsClearanceMark必填
    tax_rate = fields.Char('稅率')
    tax_amount = fields.Integer('營業稅額')
    total_amount = fields.Integer('總計金額')
