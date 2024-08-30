from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models
from odoo.exceptions import UserError


class MFPCalcAutoWizard(models.TransientModel):
    _name = 'mfp.calc.auto.wizard'
    _description = '自動(auto)計算帳單'

    # ==================== 計算帳單 ====================
    # 取得外部ID
    def _get_external_id(self, ref):
        # 使用search方法查找外部ID
        ir_model_data = self.env['ir.model.data'].sudo().search([('name', '=', ref)])
        # 如果找到，取得相對應的記錄ID
        # 如果找不到，返回None或者其他適當的值
        return ir_model_data.res_id if ir_model_data else False

    # ========== 結帳計算(含檢查) ==========
    # 參數:
    # mfp_id: 事務機ID
    def auto_calc_account_move(self, mfp_id):
        # ========== 檢查結算條件 ==========
        # 檢查事務機的結算日, 是否符合結算條件
        # 結算日
        stl_date = mfp_id.stl_date
        meter_date = mfp_id.meter_date
        # 若尚未到[下期結算日], 即未到結算日則返回
        if datetime.now().date() < stl_date:
            return False

        # ========== 計算帳單 ==========
        account_moves = self._calc_account_move(mfp_id, meter_date, stl_date)
        return account_moves

    # ========== 結帳計算 ==========
    # 定時每天晚上6:30 計算帳單
    # 目前僅知道先顯示異常, 未來優化將顯示細節問題, 通知人員先暫訂工程師, 未來將改為會計人員
    # ==== mfp (多筆) ====
    def _calc_mfps(self):
        print(f'========== iron_account start: {datetime.now()} ==========')
        # 所有事務機
        now = datetime.now().date()
        domain = ['&', ('state', '=', '1'), ('stl_date', '<=', now)]
        mfp_ids = self.env['mfp.data'].search(domain)
        print(f'iron_account mfp count: {mfp_ids.count}')
        if not mfp_ids:
            print(f'========== iron_account end: {datetime.now()} ==========')
            return

        for mfp_id in mfp_ids:
            self.env['mfp.calc.auto.wizard'].auto_calc_account_move(mfp_id)
        print(f'========== iron_account end: {datetime.now()} ==========')

    # ==== mfp (單一) ====
    def _calc_mfp(self, mfp_id, meter_date, stl_date):
        # 事務機(本身)
        date = []
        rental = mfp_id.rental
        # 記錄張數
        count = self._calc_mfp_records(mfp_id, meter_date, stl_date)
        deduct = self._calc_mfp_deduct(mfp_id)
        invalid = self._calc_mfp_invalid(mfp_id)
        black_print = count[0] - invalid[0] - deduct[0]
        color_print = count[1] - invalid[1] - deduct[1]
        large_print = count[2] - invalid[2]
        date.append(count[3])
        # 事務機(合併)
        merge_ids = mfp_id.merge_ids
        for mfp_merge in merge_ids:
            rental += mfp_merge.rental
            # 記錄張數
            count = self._calc_mfp_records(mfp_merge, meter_date, stl_date)
            black_print += count[0] - invalid[0] - deduct[0]
            color_print += count[1] - invalid[1] - deduct[1]
            large_print += count[2] - invalid[2]
            date.append(count[3])
        # 正規化 張數為負數時
        black_print = black_print if black_print > 0 else 0
        color_print = color_print if color_print > 0 else 0
        large_print = large_print if large_print > 0 else 0
        return rental, black_print, color_print, large_print, date

    # ==== mfp record (單一) ====
    # 記錄張數
    def _calc_mfp_records(self, mfp_id, meter_date, stl_date):
        # ========== 抄表紀錄 ==========
        # 從抄表記錄獲取張數
        # 上次抄表日期: meter_date
        # 結算日: stl_date
        # 黑白張數: black_print
        # 彩色張數: color_print
        # 大型張數: large_print
        black_print_start = 0
        black_print_end = 0
        color_print_start = 0
        color_print_end = 0
        large_print_start = 0
        large_print_end = 0

        domain = ['&', '&',
                  ('date', '>=', meter_date),
                  ('date', '<=', stl_date),
                  ('mfp_id', '=', mfp_id.id)]
        mfp_records = self.env['mfp.record'].sudo().search(domain, order='date asc')
        # 限制必須要兩筆以上的紀錄, 才可計算(後-前)
        if not mfp_records or len(mfp_records) < 2:
            message = '抄表紀錄不足,無法計算'
            raise UserError(message)
        date = stl_date
        description = ''  # 此描述內容
        start = True  # 此紀錄為起始紀錄
        for rec in mfp_records:
            if (rec.state == '0') and start:
                black_print_start = rec.black_print
                color_print_start = rec.color_print
                large_print_start = rec.large_print
                start = False
            elif rec.state in ['1', '3']:
                black_print_start = rec.black_print
                color_print_start = rec.color_print
                large_print_start = rec.large_print
                description = '新機' if rec.state == '1' else '換機(新裝機)'
                start = False
            elif rec.state == '2':
                date = rec.date
                black_print_end = rec.black_print
                color_print_end = rec.color_print
                large_print_end = rec.large_print
                description = '退機'
                break
            elif rec.state == '4':
                # description = '測試'
                pass
            else:
                date = rec.date
                black_print_end = rec.black_print
                color_print_end = rec.color_print
                large_print_end = rec.large_print

        # if black_print_start > black_print_end:
        #     black_print_end = black_print_start
        #     black_print_start = 0
        # if color_print_start > color_print_end:
        #     color_print_end = color_print_start
        #     color_print_start = 0
        # if large_print_start > large_print_end:
        #     large_print_end = large_print_start
        #     large_print_start = 0

        black_print = black_print_end - black_print_start
        color_print = color_print_end - color_print_start
        large_print = large_print_end - large_print_start
        return black_print, color_print, large_print, date, description

    @staticmethod
    def _calc_mfp_invalid(mfp_id):
        invalid_ids = mfp_id.invalid_ids
        black_print = 0
        color_print = 0
        large_print = 0
        for rec in invalid_ids:
            black_print += rec.black_print
            color_print += rec.color_print
            large_print += rec.large_print
        return black_print, color_print, large_print

    @staticmethod
    def _calc_mfp_deduct(mfp_id):
        return mfp_id.black_print_deduct, mfp_id.color_print_deduct

    # ==== 建立 account move ====
    def _create_account_moves(self, invoice_date, partner_id):
        odoo = self.env['account.move']
        value = {
            'invoice_date': invoice_date,
            'invoice_date_due': invoice_date + relativedelta(months=1),
            'move_type': 'out_invoice',
            'partner_id': partner_id.id,
            'invoice_user_id': 1,
        }
        # company_id 一定是創建此公司的值必定為固定值1
        account_moves = odoo.sudo().with_context(default_company_id=1).create(value)
        return account_moves

    # ==== 建立 account move line ====
    # 參數:
    # move_id: 應收憑單ID
    # name: 名稱
    # partner_id: 客戶ID
    # product_id: 產品ID
    # price_unit: 價格
    # tax: 稅金
    # ※說明:
    # 在account move 新增明細 [account_move_line]時,
    # 須結合[(0, 0, {values})] 建立view_id, values代表account.move.line的資料
    # [(0, 0, {values})]: 新增
    # [(1, id, {values})]: 更新
    # [(2, id, _)]: 移除現有的紀錄
    # [(3, id, _)]: 斷開現有紀錄之間的關聯
    # [(4, id, _)]: 添加現有id的紀錄
    # [(5, 0, 0)]: 刪除所有現有關聯
    # [(6, 0, 0)]: 替換所有紀錄之間的關聯
    def _create_account_move_line(self, move_id, name, partner_id, product_id, quantity, price_unit, tax):
        domain = ['&',
                  ('move_id', '=', move_id.id),
                  ('product_id', '=', product_id.id)]
        self.env['account.move.line'].sudo().search(domain)
        # 稅金 5%(tw_tax_sale_5), 內含稅金 5%(tw_tax_sale_inc_5)
        tax_id = self._get_external_id(tax) if len(tax) > 0 else False
        value = {
            'name': f'{name}',
            'move_id': move_id.id,
            'partner_id': partner_id.id,
            'account_id': move_id.journal_id.default_account_id.id,
            'currency_id': move_id.currency_id.id,
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'quantity': quantity,
            'tax_ids': [(4, tax_id, 0)] if tax_id else False,
            'price_unit': price_unit,
        }
        move_id.invoice_line_ids = [(0, 0, value)]

    # 更新-事務機
    @staticmethod
    def _update_mfp_date(mfp_id, stl_date, meter_date, dates):
        pay_period = int(mfp_id.pay_period)
        mfp_id.stl_date = stl_date
        mfp_id.meter_date = meter_date
        merge_ids = mfp_id.merge_ids
        for index, rec in enumerate(merge_ids):
            rec.stl_date = stl_date + relativedelta(months=pay_period)
            rec.meter_date = dates[index + 1]

    # 更新-作廢張數
    @staticmethod
    def _update_mfp_invalid(mfp_id):
        invalid_ids = mfp_id.invalid_ids
        for rec in invalid_ids:
            rec.state = '1'

    # 計算-月租費
    def _cal_rentalprice(self, move_id, partner_id, date_start, date_end, rental_price, tax, is_adv):
        if rental_price > 0:
            # 產品ID: 影印費-基本月租費
            ref_id = 'mfp.product_product_mfp_adv_rental_price' if is_adv == '1' else 'mfp.product_product_mfp_rental_price'
            product_id = self.env.ref(ref_id)
            summary = f'{"預收月租費" if is_adv == "1" else "基本月租費"}:{date_start}~{date_end}'
            self._create_account_move_line(move_id, summary,
                                           partner_id, product_id, 1, rental_price, tax)

    # 計算-超印費
    def _cal_overprice(self, move_id, partner_id, date_start, date_end, over_price, tax):
        # 超印
        if over_price > 0:
            # 產品ID: 超印費
            ref_id = 'mfp.product_product_mfp_over_price'
            product_id = self.env.ref(ref_id)
            summary = f'超印費:{date_start}~{date_end}'
            self._create_account_move_line(move_id, summary,
                                           partner_id, product_id, 1, over_price, tax)

    # 參數:
    # mfp_id: 事務機
    # meter_date: 前期抄表日期
    # stl_date: 結算日
    def _calc_account_move(self, mfp_id, meter_date, stl_date):
        invoice_date = stl_date
        # 事務機(含合併)的月租&張數
        mfp = self._calc_mfp(mfp_id, meter_date, stl_date)
        rental = mfp[0]
        black_print = mfp[1]
        color_print = mfp[2]
        large_print = mfp[3]
        dates = mfp[4]

        # 金額
        pay_period = int(mfp_id.pay_period)
        rental_price = rental * pay_period
        over_price = (mfp_id.black_print_overprice * black_print +
                      mfp_id.color_print_overprice * color_print +
                      mfp_id.large_print_overprice * large_print)
        # 明細顯示 日期範圍
        date_start = stl_date - relativedelta(months=pay_period)
        date_end = stl_date

        partner_id = mfp_id.company_id
        # 是否扣抵
        deduct = mfp_id.deduct
        # 是否預繳
        is_adv = mfp_id.is_adv
        # 是否含稅
        tax = mfp_id.tax

        # 會計
        move_id = self._create_account_moves(invoice_date, partner_id)

        # 月租/預收
        self._cal_rentalprice(move_id, partner_id, date_start, date_end, rental_price, tax, is_adv)
        # 扣抵
        over_price -= rental_price if deduct == '1' else 0
        # 超印
        self._cal_overprice(move_id, partner_id, date_start, date_end, over_price, tax)

        # 更新-結算日期
        meter_date = stl_date
        stl_date = stl_date + relativedelta(months=pay_period)
        self._update_mfp_date(mfp_id, stl_date, meter_date, dates)

        # 更新-作廢紀錄
        self._update_mfp_invalid(mfp_id)
        return move_id
