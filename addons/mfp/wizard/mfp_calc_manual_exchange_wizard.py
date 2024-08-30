from odoo import fields, models, api


class MFPCalcManualExchangeWizard(models.TransientModel):
    _inherit = 'mfp.calc.manual.wizard'
    _name = 'mfp.calc.manual.exchange.wizard'
    _description = '手動(manual)計算帳單'

    line_ids = fields.One2many('mfp.calc.exchange.line', 'calc_id', '事務機(換機)')
    return_ids = fields.One2many('mfp.calc.return.line', 'calc_id', '事務機(退機)')

    rental = fields.Integer('總月租', compute='_compute_line_ids')
    # ==== 黑白 ====
    black_print = fields.Integer('黑白-總張數', compute='_compute_line_ids')
    # ==== 彩色 ====
    color_print = fields.Integer('彩色-總張數', compute='_compute_line_ids')
    # ==== 大張 ====
    large_print = fields.Integer('A3-總張數', compute='_compute_line_ids')

    @api.depends('line_ids', 'return_ids')
    def _compute_line_ids(self):
        rental = 0
        black_print = 0
        color_print = 0
        large_print = 0
        for rec in self.line_ids:
            rental += rec.rental
            black_print += rec.black_print_count
            color_print += rec.color_print_count
            large_print += rec.large_print_count
        for rec in self.return_ids:
            rental += rec.rental
            black_print += rec.black_print_count
            color_print += rec.color_print_count
            large_print += rec.large_print_count
        self.rental = rental
        self.black_print = black_print if black_print > 0 else 0
        self.color_print = color_print if color_print > 0 else 0
        self.large_print = large_print if large_print > 0 else 0

    def calc(self):
        self.ensure_one()
        partner_id = self.company_id
        invoice_date = self.invoice_date
        line_ids = self.line_ids
        if len(line_ids) == 0:
            raise UserWarning('事務機(換機)無資料')
        return_ids = self.return_ids
        if len(return_ids) == 0:
            raise UserWarning('事務機(退機)無資料')
        # 是否扣抵
        deduct = self.deduct
        # 是否預繳
        is_adv = self.is_adv
        # 是否含稅
        tax = self.tax
        rental = self.rental
        black_print = self.black_print
        color_print = self.color_print
        large_print = self.large_print
        black_print_overprice = line_ids[0].black_print_overprice
        color_print_overprice = line_ids[0].color_print_overprice
        large_print_overprice = line_ids[0].large_print_overprice
        # 金額
        pay_period = int(self.pay_period)
        rental_price = rental * pay_period
        over_price = (black_print_overprice * black_print +
                      color_print_overprice * color_print +
                      large_print_overprice * large_print)
        # 明細顯示 日期範圍
        date_start = line_ids[0].date_start
        date_end = line_ids[0].date_end

        # 會計
        move_id = self._create_account_moves(invoice_date, partner_id)

        # 月租/預收
        self._cal_rentalprice(move_id, partner_id, date_start, date_end, rental_price, tax, is_adv)
        # 扣抵
        over_price -= rental_price if deduct == '1' else 0
        # 超印
        self._cal_overprice(move_id, partner_id, date_start, date_end, over_price, tax)

        # 更新-事務機(結算, 作廢, 抄表)
        self._update_mfps(line_ids)

        # 更新-事務機(結算, 作廢, 抄表)
        self._update_mfps(return_ids)
        return move_id


class MFPCalcExchangeLine(models.TransientModel):
    _inherit = 'mfp.calc.line'
    _name = 'mfp.calc.exchange.line'
    _description = '計算帳單'

    calc_id = fields.Many2one('mfp.calc.manual.exchange.wizard', '計算帳單')


class MFPCalcReturnLine(models.TransientModel):
    _inherit = 'mfp.calc.line'
    _name = 'mfp.calc.return.line'
    _description = '計算帳單'

    calc_id = fields.Many2one('mfp.calc.manual.exchange.wizard', '計算帳單')
