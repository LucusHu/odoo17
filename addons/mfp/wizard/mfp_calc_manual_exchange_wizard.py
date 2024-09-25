from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class MFPCalcManualExchangeWizard(models.TransientModel):
    _inherit = 'mfp.calc.manual.wizard'
    _name = 'mfp.calc.manual.exchange.wizard'
    _description = '手動(manual)計算帳單'

    # line_ids = fields.One2many('mfp.calc.line', 'calc_id', '事務機(換機)')
    # return_ids = fields.One2many('mfp.calc.return.line', 'calc_id', '事務機(退機)')

    # rental = fields.Integer('總月租', compute='_compute_line_ids')
    # # ==== 黑白 ====
    # black_print = fields.Integer('黑白-總張數', compute='_compute_line_ids')
    # # ==== 彩色 ====
    # color_print = fields.Integer('彩色-總張數', compute='_compute_line_ids')
    # # ==== 大張 ====
    # large_print = fields.Integer('A3-總張數', compute='_compute_line_ids')

    # @api.depends('line_ids', 'return_ids')
    # def _compute_line_ids(self):
    #     rental = 0
    #     black_print = 0
    #     color_print = 0
    #     large_print = 0
    #     for rec in self.line_ids:
    #         rental += rec.rental
    #         black_print += rec.black_print_count
    #         color_print += rec.color_print_count
    #         large_print += rec.large_print_count
    #     for rec in self.return_ids:
    #         rental += rec.rental
    #         black_print += rec.black_print_count
    #         color_print += rec.color_print_count
    #         large_print += rec.large_print_count
    #     self.rental = rental
    #     self.black_print = black_print if black_print > 0 else 0
    #     self.color_print = color_print if color_print > 0 else 0
    #     self.large_print = large_print if large_print > 0 else 0

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


# class MFPCalcExchangeLine(models.TransientModel):
#     _inherit = 'mfp.calc.line'
#     _name = 'mfp.calc.exchange.line'
#     _description = '計算帳單'
#
#     calc_id = fields.Many2one('mfp.calc.manual.exchange.wizard', '計算帳單')
#
#
# class MFPCalcReturnLine(models.TransientModel):
#     _inherit = 'mfp.calc.line'
#     _name = 'mfp.calc.return.line'
#     _description = '計算帳單'
#
#     calc_id = fields.Many2one('mfp.calc.manual.exchange.wizard', '計算帳單')
