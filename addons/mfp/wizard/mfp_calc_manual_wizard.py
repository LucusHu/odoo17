from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class MFPCalcManualWizard(models.TransientModel):
    _inherit = 'mfp.calc.auto.wizard'
    _name = 'mfp.calc.manual.wizard'
    _description = '手動(manual)計算帳單'

    line_ids = fields.One2many('mfp.calc.line', 'calc_id', '事務機清單')

    company_id = fields.Many2one('res.partner', '公司名稱', required=True,
                                 domain="['&', '&',"
                                        "('user_ids', '=', False),"
                                        "('company_id', '=', False),"
                                        "('parent_id', '=', False)]")
    company_number = fields.Char('客戶編號', related='company_id.number')
    invoice_date = fields.Date('發票日期', default=fields.Date.today(), required=True)

    rental_price = fields.Integer('總月租', compute='_compute_line_ids')
    # ==== 黑白 ====
    black_print = fields.Integer('黑白-總張數', compute='_compute_line_ids')
    # ==== 彩色 ====
    color_print = fields.Integer('彩色-總張數', compute='_compute_line_ids')
    # ==== 大張 ====
    large_print = fields.Integer('A3-總張數', compute='_compute_line_ids')

    @api.depends('line_ids')
    def _compute_line_ids(self):
        for record in self:
            rental_price = 0
            black_print = 0
            color_print = 0
            large_print = 0
            for rec in record.line_ids:
                rental_price += rec.rental_price
                black_print += rec.black_print_count
                color_print += rec.color_print_count
                large_print += rec.large_print_count
            record.rental_price = rental_price
            record.black_print = black_print if black_print > 0 else 0
            record.color_print = color_print if color_print > 0 else 0
            record.large_print = large_print if large_print > 0 else 0

    # 將資料寫回至紀錄(record)
    def _write_mfp_record(self, mfp_id, date, black_print, color_print, large_print):
        ref_id = 'mfp.mfp_record_category_manual'
        category_manual = self.env.ref(ref_id).id

        odoo_m = self.env['mfp.record']
        domain = ['&',
                  ('mfp_id', '=', mfp_id.id),
                  ('date', '=', date)]
        mfp_record = odoo_m.sudo().search(domain, limit=1)
        if mfp_record:
            mfp_record.update({
                'black_print': black_print,
                'color_print': color_print,
                'large_print': large_print,
                'category_id': [(6, 0, [category_manual])],
            })
        else:
            odoo_m.create({
                'company_id': mfp_id.company_id.id if mfp_id.company_id else False,
                'mfp_id': mfp_id.id,
                'date': date,
                'black_print': black_print,
                'color_print': color_print,
                'large_print': large_print,
                'category_id': [(6, 0, [category_manual])],
            })

    def calc_start(self):
        self.ensure_one()
        self.manual_calc_account_move()

    def manual_calc_account_move(self):
        self.ensure_one()
        self._calc_account_move()

    def _calc_account_move(self):
        # ========== 發票(應收憑單)草稿 ==========
        # 客戶
        partner_id = self.company_id
        # 發票日期
        invoice_date = self.invoice_date
        # 事務機
        line_ids = self.line_ids
        if len(line_ids) == 0:
            raise UserWarning('事務機(合併)無資料')

        # 含稅(取第一位設定為主
        tax = line_ids[0].tax
        # 會計
        move_id = self._create_account_moves(invoice_date, partner_id)

        rental_price = self.rental_price

        # 明細顯示 日期範圍
        date_start = line_ids[0].date_start
        date_end = line_ids[0].date_end
        # ==== 月費結算 ====
        # 預繳
        is_adv = line_ids[0].is_adv
        # 月租/預收
        self._cal_rentalprice(move_id, partner_id, date_start, date_end, rental_price, tax, is_adv)

        for line_id in line_ids:
            date_start = line_id.date_start
            date_end = line_id.date_end
            # rental_begin = date_start
            # rental_finish = date_end

            mfp_id = line_id.mfp_id
            pay_period = int(mfp_id.pay_period)
            rental_date = mfp_id.rental_date
            if rental_date < date_end:
                rental_date = rental_date + relativedelta(months=pay_period)
                # 更新事務機月費資料
                self._update_mfp_rental_date(mfp_id, rental_date)

        # ==== 超印費結算 ====
        # 扣抵(取第一位設定為主
        deduct = line_ids[0].deduct

        black_print = self.black_print
        color_print = self.color_print
        large_print = self.large_print
        # 價格(取第一位設定為主
        black_print_overprice = line_ids[0].black_print_overprice
        color_print_overprice = line_ids[0].color_print_overprice
        large_print_overprice = line_ids[0].large_print_overprice

        # 金額
        over_price = (black_print_overprice * black_print +
                      color_print_overprice * color_print +
                      large_print_overprice * large_print)

        # 扣抵
        over_price -= rental_price if deduct == '1' else 0
        # 超印
        self._cal_overprice(move_id, partner_id, date_start, date_end, over_price, tax, rental_price)

        for line_id in line_ids:
            date_start = line_id.date_start
            date_end = line_id.date_end

            mfp_id = line_id.mfp_id
            pay_period = int(mfp_id.pay_period)

            # 事務機清單
            self._create_account_print_line(move_id, mfp_id, date_start, date_end,
                                            line_id.rental, pay_period,
                                            line_id.black_print_start, line_id.black_print_end,
                                            line_id.black_print_invalid,
                                            line_id.color_print_start, line_id.color_print_end,
                                            line_id.color_print_invalid,
                                            line_id.large_print_start, line_id.large_print_end,
                                            line_id.large_print_invalid)
            # 更新-抄表紀錄
            self._write_mfp_record(mfp_id, date_start,
                                   line_id.black_print_start, line_id.color_print_start, line_id.large_print_start)
            self._write_mfp_record(mfp_id, date_end,
                                   line_id.black_print_end, line_id.color_print_end, line_id.large_print_end)

            # 更新-結算日
            stl_date = mfp_id.stl_date
            if stl_date < date_end:
                stl_date = stl_date + relativedelta(months=pay_period)
                self._update_mfp_stl_date(mfp_id, stl_date)

            # 更新-實際紀錄日
            meter_date = mfp_id.meter_date
            if meter_date < date_end:
                meter_date = date_end
                self._update_mfp_meter_date(mfp_id, meter_date)

            # 清除作廢紀錄
            invalid_ids = line_id.invalid_ids
            for rec in invalid_ids:
                rec.state = '1'

        return move_id

    # 計算並前往會計
    def btn_calc_account(self):
        self.ensure_one()
        self.calc_start()
        # 返回動作以關閉視窗
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        return action

    # 計算並新建立
    def btn_calc_new(self):
        self.ensure_one()
        self.calc_start()
        # 返回動作以打開新的視窗
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mfp.calc.manual.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('mfp.view_mfp_calc_manual_wizard_form').id,
        }


class MFPCalcLine(models.TransientModel):
    # _inherit = 'mfp.data'
    _name = 'mfp.calc.line'
    _description = '計算帳單'

    calc_id = fields.Many2one('mfp.calc.manual.wizard', '計算帳單')

    company_id = fields.Many2one('res.partner', '公司名稱', required=True,
                                 domain="['&', '&',"
                                        "('user_ids', '=', False),"
                                        "('company_id', '=', False),"
                                        "('parent_id', '=', False)]")

    company_number = fields.Char('客戶編號', related='company_id.number')

    mfp_id = fields.Many2one('mfp.data', '事務機', required=True,
                             domain="[('company_id', '=?', company_id)]")
    invalid_ids = fields.One2many('mfp.invalid.record', string='作廢筆數', related='mfp_id.invalid_ids')
    kind = fields.Selection([('0', '一般'), ('1', '合併'), ('2', '換機'), ('3', '退機')], '類型', default='0')
    merge_ids = fields.Many2many('mfp.data', string='合併', related='mfp_id.merge_ids')
    # merge_id = fields.Many2many('mfp.data', string='合併於', related='mfp_id.merge_id')
    contract_ids = fields.Many2many('mfp.contract', string='合約類型',
                                    related='mfp_id.contract_ids')
    # rental = fields.Integer('月租', related='mfp_id.rental')
    rental = fields.Integer('月租')
    rental_price = fields.Integer('總月租', compute='_compute_rental_price')

    @api.depends('pay_period', 'rental')
    def _compute_rental_price(self):
        for rec in self:
            pay_period = int(rec.pay_period)
            rec.rental_price = rec.rental * pay_period

    # pay_period = fields.Selection([('1', '每月'), ('2', '兩個月'), ('3', '每季(三個月)'),
    #                                ('6', '半年'), ('12', '每年')],
    #                               '結算期數', related='calc_id.pay_period')
    deduct = fields.Selection([('0', '否'), ('1', '是')], '扣抵月租', related='mfp_id.deduct')
    pay_period = fields.Selection([('1', '每月'), ('2', '兩個月'), ('3', '每季(三個月)'),
                                   ('6', '半年'), ('12', '每年')],
                                  '結算期數', related='mfp_id.pay_period')

    is_adv = fields.Selection([('0', '否'), ('1', '是')], '預收月租', related='mfp_id.is_adv')
    tax = fields.Selection([('no_tax', '未稅'), ('tw_tax_sale_5', '稅金5%'), ('tw_tax_sale_inc_5', '稅金5%-內含')],
                           '稅額', related='mfp_id.tax')

    @api.onchange('calc_id')
    def _onchange_calc_id(self):
        self.company_id = self.calc_id.company_id

    # 作廢張數
    def _calc_invalid(self, _mfp_id):
        records = _mfp_id.invalid_ids
        _record = {
            'black': {'invalid': 0},
            'color': {'invalid': 0},
            'large': {'invalid': 0},
        }
        for rec in records:
            _record['black']['invalid'] += rec.black_print
            _record['color']['invalid'] += rec.color_print
            _record['large']['invalid'] += rec.large_print
        return _record

    @api.onchange('mfp_id')
    def _onchange_mfp(self):
        mfp_id = self.mfp_id
        if mfp_id:
            self.company_id = mfp_id.company_id
            # period = int(self.pay_period)
            self.rental = mfp_id.rental
            # self.date_start = mfp_id.stl_date - relativedelta(months=period)
            self.date_start = mfp_id.meter_date
            self.date_end = mfp_id.stl_date

            # self.black_print_deduct = mfp_id.black_print_deduct
            # self.color_print_deduct = mfp_id.color_print_deduct

            # 作廢張數
            invalids = self._calc_invalid(mfp_id)
            self.black_print_invalid = invalids['black']['invalid']
            self.color_print_invalid = invalids['color']['invalid']
            self.large_print_invalid = invalids['large']['invalid']

    # ========== 張數 ==========
    # ==== 起始 ====
    date_start = fields.Date('起算日期', required=True)
    black_print_start = fields.Integer('黑白-起算張數')
    color_print_start = fields.Integer('彩色-起算張數')
    large_print_start = fields.Integer('A3-起算張數')

    # 擷取相關抄表紀錄
    @api.onchange('date_start')
    def _onchange_date_start(self):
        mfp_id = self.mfp_id
        date = self.date_start
        if mfp_id:
            # 起算日期
            domain = ['&',
                      ('date', '=', date),
                      ('mfp_id', '=', mfp_id.id)]
            mfp_records = self.env['mfp.record'].sudo().search(domain, order='date asc', limit=1)

            self.black_print_start = mfp_records.black_print if mfp_records else 0
            self.color_print_start = mfp_records.color_print if mfp_records else 0
            self.large_print_start = mfp_records.large_print if mfp_records else 0
        else:
            self.black_print_start = 0
            self.color_print_start = 0
            self.large_print_start = 0

    # ==== 結束 ====
    date_end = fields.Date('結算日期', required=True)
    black_print_end = fields.Integer('黑白-結算張數')
    color_print_end = fields.Integer('彩色-結算張數')
    large_print_end = fields.Integer('A3-結算張數')

    # 擷取相關抄表紀錄
    @api.onchange('date_end')
    def _onchange_date_end(self):
        mfp_id = self.mfp_id
        date = self.date_end
        if mfp_id:
            # 結算日期
            domain = ['&',
                      ('date', '=', date),
                      ('mfp_id', '=', mfp_id.id)]
            mfp_records = self.env['mfp.record'].sudo().search(domain, order='date asc', limit=1)

            self.black_print_end = mfp_records.black_print if mfp_records else 0
            self.color_print_end = mfp_records.color_print if mfp_records else 0
            self.large_print_end = mfp_records.large_print if mfp_records else 0
        else:
            self.black_print_start = 0
            self.color_print_start = 0
            self.large_print_start = 0

    # ==== 黑白 ====
    black_print_invalid = fields.Integer('黑白-作廢張數', readonly=True)
    black_print_overprice = fields.Float('黑白-超印價格', related='mfp_id.black_print_overprice')
    black_print_deduct = fields.Integer('黑白-贈送張數', related='mfp_id.black_print_deduct')
    black_print_count = fields.Integer('黑白-列印張數', compute='_compute_black_print')

    # ==== 彩色 ====
    color_print_invalid = fields.Integer('彩色-作廢張數', readonly=True)
    color_print_overprice = fields.Float('彩色-超印價格', related='mfp_id.color_print_overprice')
    color_print_deduct = fields.Integer('彩色-贈送張數', related='mfp_id.color_print_deduct')
    color_print_count = fields.Integer('彩色-列印張數', compute='_compute_color_print')

    # ==== 大張 ====
    large_print_invalid = fields.Integer('A3-作廢張數', readonly=True)
    large_print_overprice = fields.Float('A3-超印價格', related='mfp_id.large_print_overprice')
    large_print_count = fields.Integer('A3-列印張數', compute='_compute_large_print')

    @api.depends('pay_period', 'black_print_start', 'black_print_end', 'black_print_invalid')
    def _compute_black_print(self):
        for rec in self:
            period = int(rec.pay_period)
            end = rec.black_print_end
            start = rec.black_print_start
            deduct = rec.black_print_deduct
            invalid = rec.black_print_invalid
            count = end - start - (deduct * period) - invalid
            rec.black_print_count = count

    @api.depends('pay_period', 'color_print_start', 'color_print_end', 'color_print_invalid')
    def _compute_color_print(self):
        for rec in self:
            period = int(rec.pay_period)
            end = rec.color_print_end
            start = rec.color_print_start
            deduct = rec.color_print_deduct
            invalid = rec.color_print_invalid
            count = end - start - (deduct * period) - invalid
            rec.color_print_count = count

    @api.depends('pay_period', 'large_print_start', 'large_print_end', 'large_print_invalid')
    def _compute_large_print(self):
        for rec in self:
            # period = int(self.pay_period)
            end = rec.large_print_end
            start = rec.large_print_start
            # deduct = self.large_print_deduct
            invalid = rec.large_print_invalid
            # count = end - start - (deduct * period) - invalid
            count = end - start - invalid
            rec.large_print_count = count

    print_count = fields.Char('張數(C/B/L)', compute='_compute_print_count')

    @api.depends('black_print_count', 'color_print_count', 'large_print_count')
    def _compute_print_count(self):
        for rec in self:
            black = rec.black_print_count
            color = rec.color_print_count
            large = rec.large_print_count
            rec.print_count = f'{color}/{black}/{large}'
