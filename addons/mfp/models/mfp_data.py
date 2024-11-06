from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# 事務機: MFP's Structure
class MFPData(models.Model):
    _name = 'mfp.data'
    _description = 'MFP Data'
    _order = 'company_number'

    # ========== 合併 ==========

    merge_ids = fields.Many2many('mfp.data', 'mfp_merge_rel', 'mfp_id', 'merge_id', '合併計費',
                                 domain="[('id', '!=', id)]")
    merge_id = fields.Many2many('mfp.data', 'mfp_merge_rel', 'merge_id', 'mfp_id', '已合併至',
                                domain="[('id', '!=', id)]")
    # ========== 抄表事件 ==========
    record_ids = fields.One2many('mfp.record', 'mfp_id', '抄表紀錄', readonly=True)

    # ========== 告警事件 ==========
    alert_ids = fields.One2many('mfp.alert.record', 'mfp_id', '告警訊息', readonly=True)

    # ========== 作廢張數 ==========
    invalid_ids = fields.One2many('mfp.invalid.record', 'mfp_id', '作廢筆數',
                                  domain=[('state', '=', '0')])
    # ========== 客戶資料 ==========
    company_id = fields.Many2one('res.partner', '公司名稱', required=True,
                                 domain="['&', '&',"
                                        "('user_ids', '=', False),"
                                        "('company_id', '=', False),"
                                        "('parent_id', '=', False)]", ondelete='cascade')
    place_id = fields.Many2one('mfp.place', '裝機地點', required=True,
                               domain="[('company_id', '=?', company_id)]")
    user_id = fields.Many2one('res.users', '維護工程師')
    proxy_user = fields.Many2one('res.users', '代理工程師')

    # ========== 帳務通知 ==========
    # notify_ids = fields.Many2many('res.partner', string='帳務通知',
    #                               domain="[('parent_id', '=?', company_id)]")

    # ========== 事務機 ==========
    brand_id = fields.Many2one('mfp.brand', '廠牌',
                               required=True)
    model_id = fields.Many2one('mfp.brand.model', '型號',
                               domain="[('brand_id', '=?', brand_id)]",
                               required=True)

    name = fields.Char('事務機名稱')
    company_name = fields.Char('公司名稱', related='company_id.name')
    company_number = fields.Char('客戶編號', related='company_id.number')
    # company_number = fields.Char('客戶編號', compute='_compute_company', store=True)

    # @api.depends('company_id')
    # def _compute_company(self):
    #     for record in self:
    #         record.company_number = record.company_id.number

    printer_name = fields.Char('列印機名稱')
    serial_number = fields.Char('機器號碼')
    mac = fields.Char('MAC', readonly=True)
    ip = fields.Char('IP位址')
    # 若為[新機]則 下月開始計費(月費&張數)
    # 若為[退機]則 下月結束計費(月費&張數)
    # 若為[換機]則 下月開始計費(月費), 超印的計費依舊(張數)
    # status = fields.Selection([('0', '一般'), ('1', '新裝機'), ('2', '退機'), ('3', '換機')],
    #                           '狀態')

    # ========== contract ==========
    contract_start = fields.Date('合約開始', default=fields.Date.today(), required=True)
    contract_end = fields.Date('合約結束', default=lambda self: self._default_contract_end(), required=True)
    contract_ids = fields.Many2many('mfp.contract', string='合約類型')

    def _default_contract_end(self):
        return fields.Date.today() + relativedelta(years=1)

    deposit = fields.Integer('機器押金', default=0, required=True)

    # ========== 抄表日 ==========
    # 抄表日 & 前後X日
    meter_day = fields.Integer('抄表日', default=1, required=True, help='伴隨結算日期連動')
    # meter_day = fields.Integer('抄表日', compute='_compute_meter', help='伴隨結算日期連動')
    # meter = fields.Integer()
    meter_before = fields.Integer('抄表日前X日', default=2)
    meter_after = fields.Integer('抄表日後X日', default=2)
    meter_date = fields.Date('抄表起算', default=lambda self: self._default_stl_date(), required=True,
                             help='初次安裝選擇安裝日, 其次則選擇前次結算日算(抄表紀錄，起算日期)')

    # ========== 費用 ==========
    rental = fields.Integer('月租', default=0, required=True)
    deduct = fields.Selection([('0', '否'), ('1', '是')], '扣抵月租', default='1', required=True)

    # ========== 結算 ==========
    pay_period = fields.Selection([('1', '每月'), ('2', '兩個月'), ('3', '每季(三個月)'),
                                   ('6', '半年'), ('12', '每年')],
                                  '結算期數', default='1', required=True)

    is_adv = fields.Selection([('0', '否'), ('1', '是')], '預收月租', default='1', required=True)
    tax = fields.Selection(
        [('tw_no_tax_sale', '未稅'), ('tw_tax_sale_5', '稅金5%'), ('tw_tax_sale_inc_5', '稅金5%-內含')],
        '稅額', default='tw_tax_sale_5', required=True)
    # stl_prev_date = fields.Date('前期結算日', default=lambda self: self._default_date())
    stl_date = fields.Date('結算起算', default=lambda self: self._default_stl_date(), required=True,
                           help='(結算帳單，起算日期)')
    stl_next_date = fields.Date('下次結算', compute='_compute_stl_next_date', store=True)
    rental_date = fields.Date('預收起算', default=lambda self: self._default_rental_date(), required=True,
                              help='(預收月租，起算日期)')
    rental_next_date = fields.Date('下次預收', compute='_compute_rental_next_date', store=True)

    def _default_stl_date(self):
        date = datetime.now().date()
        year = date.year
        month = date.month
        day = 1
        return datetime(year, month, day)

    def _default_rental_date(self):
        date = datetime.now().date()
        year = date.year
        month = date.month
        day = 1
        return datetime(year, month, day)

    @api.depends('stl_date', 'pay_period')
    def _compute_stl_next_date(self):
        for record in self:
            pay_period = int(record.pay_period)
            record.stl_next_date = record.stl_date + relativedelta(months=pay_period)

    @api.depends('rental_date', 'pay_period')
    def _compute_rental_next_date(self):
        for record in self:
            pay_period = int(record.pay_period)
            record.rental_next_date = record.rental_date + relativedelta(months=pay_period)

    @api.depends('stl_date')
    def _compute_meter(self):
        for record in self:
            stl_date = record.stl_date
            if stl_date:
                date_obj = fields.Date.from_string(stl_date)
                year = date_obj.year
                month = date_obj.month
                day = date_obj.day
                self.meter_day = day

    # ========== 張數 ==========
    # ==== 黑白 ====
    # black_print_invalid = fields.Integer('黑白-作廢張數')
    black_print_overprice = fields.Float('黑白-超印價格', default=0, required=True)
    black_print_deduct = fields.Integer('黑白-贈送張數', default=0, required=True)
    # ==== 彩色 ====
    # color_print_invalid = fields.Integer('彩色-作廢張數')
    color_print_overprice = fields.Float('彩色-超印價格', default=0, required=True)
    color_print_deduct = fields.Integer('彩色-贈送張數', default=0, required=True)
    # ==== 大張 ====
    # large_print_invalid = fields.Integer('A3-作廢張數')
    large_print_overprice = fields.Float('A3大尺寸價格', default=0, required=True)

    black_overprice = fields.Float('黑白-超印價格', compute='_compute_overprice')
    color_overprice = fields.Float('彩色-超印價格', compute='_compute_overprice')
    large_overprice = fields.Float('A3-超印價格', compute='_compute_overprice')
    merge_stl_date = fields.Date('收費起算', compute='_compute_overprice')
    merge_stl_next_date = fields.Date('收費結算', compute='_compute_overprice')
    merge_rental_date = fields.Date('預收起算', compute='_compute_overprice')
    merge_rental_next_date = fields.Date('預收結算', compute='_compute_overprice')

    # 計算
    def _compute_overprice(self):
        for record in self:
            merge_id = record.merge_id
            record.black_overprice = merge_id.black_overprice if merge_id else record.black_print_overprice
            record.color_overprice = merge_id.color_overprice if merge_id else record.color_print_overprice
            record.large_overprice = merge_id.large_overprice if merge_id else record.large_print_overprice
            record.merge_stl_date = merge_id.stl_date if merge_id else record.stl_date
            record.merge_stl_next_date = merge_id.stl_next_date if merge_id else record.stl_next_date
            record.merge_rental_date = merge_id.rental_date if merge_id else record.rental_date
            record.merge_rental_next_date = merge_id.rental_next_date if merge_id else record.rental_next_date
            # ========== 碳粉/滾筒 ==========

    # ==== 碳粉 ====
    toner_black = fields.Float('碳粉-黑色', readonly=True)
    toner_cyan = fields.Float('碳粉-青色', readonly=True)
    toner_magenta = fields.Float('碳粉-洋紅色', readonly=True)
    toner_yellow = fields.Float('碳粉-黃色', readonly=True)
    toner = fields.Char('碳粉(B-C-M-Y)', compute='_compute_toner')

    @api.depends('toner_black', 'toner_cyan', 'toner_magenta', 'toner_yellow')
    def _compute_toner(self):
        for record in self:
            record.toner = f""
            record.toner += f"{int(record.toner_black * 100)}%-"
            record.toner += f"{int(record.toner_cyan * 100)}%-"
            record.toner += f"{int(record.toner_magenta * 100)}%-"
            record.toner += f"{int(record.toner_yellow * 100)}%"

    # ==== 滾筒 ====
    drum_black = fields.Float('滾筒-黑色', readonly=True)
    drum_cyan = fields.Float('滾筒-青色', readonly=True)
    drum_magenta = fields.Float('滾筒-洋紅色', readonly=True)
    drum_yellow = fields.Float('滾筒-黃色', readonly=True)
    drum = fields.Char('滾筒(B-C-M-Y)', compute='_compute_drum')

    @api.depends('drum_black', 'drum_cyan', 'drum_magenta', 'drum_yellow')
    def _compute_drum(self):
        for record in self:
            record.drum = f""
            record.drum += f"{int(record.drum_black * 100)}%-"
            record.drum += f"{int(record.drum_cyan * 100)}%-"
            record.drum += f"{int(record.drum_magenta * 100)}%-"
            record.drum += f"{int(record.drum_yellow * 100)}%"

    state = fields.Selection([('0', '停用'), ('1', '啟用')],
                             '狀態', default='1', required=True)
    description = fields.Text('說明')
    tooltip_ids = fields.Many2many('mfp.tooltip', string='提示')

    def action_invalid(self):
        return {
            'name': '作廢張數 Paper Invalid',
            'res_model': 'mfp.invalid.record',
            'view_mode': 'form',
            'view_id': self.env.ref('mfp.view_mfp_invalid_record_form').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_mfp_id': self.id,  # 这里假设 mfp_id 是一个 Many2one 字段
            },
        }

    def action_standby(self):
        place_id = self.env.ref('mfp.mfp_place_main_company')

        domain = [('id', '=', self.id)]
        record = self.env['mfp.data'].sudo().search(domain)
        record.write({
            'company_id': self.env.user.company_id.id,
            'place_id': place_id.id
        })

    # ========== iron ==========
    # 定時每天晚上8:00 檢查未有抄表紀錄之事務機
    # 並發出Line警告
    def iron_noreocrd(self):
        print(f'iron_noreocrd {datetime.now()}')
        # 所有事務機
        domain = [('state', '=', '1')]
        records = self.env['mfp.data'].sudo().search(domain)
        if not records:
            return
        now = datetime.now().date()

        for record in records:
            stl_date = record.stl_date
            meter_before = record.meter_before
            meter_after = record.meter_after
            date1 = stl_date - timedelta(days=meter_before)
            date2 = stl_date + timedelta(days=meter_after)
            if now < date1 or now > date2:
                continue

            user_id = record.user_id
            proxy_user = record.proxy_user
            name = record.name
            company_name = record.company_id.name if record.company_id else ''
            place_name = record.place_id.name if record.place_id else ''

            # notify_name = f'事務機無資料 公司:{company_name} {now.year}-{now.month}-{now.day} {name}'
            notify_message = f'事件:事務機:{name} 未在預定日期{date1} ~ {date2}中獲取到張數資料, 請手動補資料,自行出帳 \r\n' \
                             f'公司:{company_name} \r\n' \
                             f'裝機地點:{place_name} \r\n' \
                             f'事務機:{name}'
            if user_id and user_id.line_token:
                user_id.line_to(notify_message)
            if proxy_user and proxy_user.line_token:
                proxy_user.line_to(notify_message)


class MFPPrintInvalid(models.Model):
    _name = 'mfp.invalid.record'
    _description = 'MFP Print Invalid Record'

    company_id = fields.Many2one('res.partner', '公司名稱', related='mfp_id.company_id')
    company_number = fields.Char('客戶編號', related='company_id.number')
    company_name = fields.Char('公司名稱', related='company_id.name')
    place_id = fields.Many2one('mfp.place', '裝機地點', related='mfp_id.place_id')
    mfp_id = fields.Many2one('mfp.data', '事務機', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', '建立者', default=lambda self: self._default_user_id())

    def _default_user_id(self):
        return self.env.user.id

    black_print = fields.Integer('黑白張數', default=0, required=True)
    color_print = fields.Integer('彩色張數', default=0, required=True)
    large_print = fields.Integer('A3張數', default=0, required=True)

    date = fields.Date('日期', default=fields.Date.today(), required=True)
    invalid_reason = fields.Html('作廢事由', required=True)
    state = fields.Selection([('0', '未完成'), ('1', '已完成')], '狀態',
                             default='0', required=True)
