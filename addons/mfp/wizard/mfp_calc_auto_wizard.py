from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class MFPCalcAutoWizard(models.TransientModel):
    _name = 'mfp.calc.auto.wizard'
    _description = '自動(auto)計算帳單'

    # ==================== 計算帳單 ====================
    # 取得外部ID
    def ref_id(self, ref):
        # 使用search方法查找外部ID
        domain = ['&',
                  ('model', '=', 'account.tax'),
                  ('name', 'ilike', ref)]
        ir_model_data = self.env['ir.model.data'].sudo().search(domain, limit=1)
        # 如果找到，取得相對應的記錄ID
        # 如果找不到，返回None或者其他適當的值
        return ir_model_data.res_id if ir_model_data else False

    # ========== 結帳計算(含檢查) ==========
    # 參數:
    # mfp_id: 事務機ID
    # def auto_calc_account_move(self, mfp_id):
    #     # ========== 檢查結算條件 ==========
    #     # 檢查事務機的結算日, 是否符合結算條件
    #     # 月租結算日
    #     rental_date = mfp_id.rental_date
    #     # 超印結算日
    #     stl_date = mfp_id.stl_date
    #     # 實際紀錄抄表日
    #     meter_date = mfp_id.meter_date
    #     # ========== 計算帳單 ==========
    #     return self._calc_account_move(mfp_id, rental_date, meter_date, stl_date)
    # ========== 結帳計算 ==========
    # 定時每天晚上6:30 計算帳單
    # 目前僅知道先顯示異常, 未來優化將顯示細節問題, 通知人員先暫訂工程師, 未來將改為會計人員
    # ==== mfp (多筆) ====
    def calc_start(self):
        _logger.info(f"========== iron_account start: {datetime.now()} ==========")
        self.auto_calc_adv_rental()
        self.auto_calc_normal()
        _logger.info(f'========== iron_account end: {datetime.now()} ==========')

    def auto_calc_adv_rental(self):
        _logger.info(f"========== calc rental start: {datetime.now()} ==========")
        # 所有事務機
        now = datetime.now().date()
        companies = self.env['res.company'].search([('partner_id', '!=', False)]).mapped('partner_id')
        domain = ['&', '&', '&', '&',
                  ('company_id', 'not in', companies.ids),
                  ('state', '=', '1'),
                  # ('ip', '!=', False),  # 使用 False 而不是 'False' 字符串
                  ('merge_id', '=', False),
                  ('is_adv', '=', '1'),
                  ('rental_next_date', '<=', now)]
        _logger.info(f"domain=> {domain}")
        mfp_ids = self.env['mfp.data'].search(domain)
        _logger.info(f'calc rental count: {len(mfp_ids)}')

        [self.env['mfp.calc.auto.wizard']._calc_adv_rental(mfp_id) for mfp_id in mfp_ids] if mfp_ids else False
        _logger.info(f'========== calc rental end: {datetime.now()} ==========')

    def auto_calc_normal(self):
        _logger.info(f"========== calc overprice start: {datetime.now()} ==========")
        # 所有事務機
        now = datetime.now().date()
        companies = self.env['res.company'].search([('partner_id', '!=', False)]).mapped('partner_id')
        domain = ['&', '&', '&',
                  ('company_id', 'not in', companies.ids),
                  ('state', '=', '1'),
                  # ('ip', '!=', False),  # 使用 False 而不是 'False' 字符串
                  ('merge_id', '=', False),
                  # ('is_adv', '=', '0'),
                  ('stl_next_date', '<=', now)]
        _logger.info(f"domain=> {domain}")
        mfp_ids = self.env['mfp.data'].search(domain)
        _logger.info(f'calc overprice count: {len(mfp_ids)}')

        [self.env['mfp.calc.auto.wizard']._calc_normal(mfp_id) for mfp_id in mfp_ids] if mfp_ids else False
        _logger.info(f'========== calc overprice end: {datetime.now()} ==========')

    # ==== 計算張數(將列印張數&贈送張數&作廢張數做相減後的計算結果(含合併) ====
    def _calc_sheet(self, mfp_id, meter_date, stl_date):
        _logger.info(f'===== _calc_sheet start =====')
        _logger.info(f"mfp_id<={mfp_id.name}")
        _logger.info(f"meter_date<={meter_date}")
        _logger.info(f"stl_date<={stl_date}")
        # 記錄張數
        record = self._calc_printer(mfp_id, meter_date, stl_date)
        _logger.info(f"len=>{len(record) if record else 0}")
        if not record:
            return False
        # 更新-結算日期
        self._update_mfp_meter_date(mfp_id, record['date']['end'])
        # ========== ==========
        # 事務機(合併)
        merge_ids = mfp_id.merge_ids
        _logger.info(f'=== _calc_sheet merge start ===')
        _logger.info(f"len=>{len(merge_ids) if merge_ids else 0}")
        for mfp_merge in merge_ids:
            _logger.info(f"mfp_id<={mfp_merge.name}")
            _logger.info(f"meter_date<={meter_date}")
            _logger.info(f"stl_date<={stl_date}")
            # 記錄張數
            m_record = self._calc_printer(mfp_merge, meter_date, stl_date)
            _logger.info(f"len=>{len(record) if record else 0}")
            if not m_record:
                continue
            # 更新-結算日期
            self._update_mfp_meter_date(mfp_merge, m_record['date']['end'])

            record['black']['count'] += m_record['black']['count']
            record['color']['count'] += m_record['color']['count']
            record['large']['count'] += m_record['large']['count']
            record['black']['deduct'] += m_record['black']['deduct']
            record['color']['deduct'] += m_record['color']['deduct']
            record['large']['deduct'] += m_record['large']['deduct']
            record['black']['invalid'] += m_record['black']['invalid']
            record['color']['invalid'] += m_record['color']['invalid']
            record['large']['invalid'] += m_record['large']['invalid']
        _logger.info(f'=== _calc_sheet merge end ===')
        record['black']['sum'] = record['black']['count'] - record['black']['invalid'] - record['black']['deduct']
        record['color']['sum'] = record['color']['count'] - record['color']['invalid'] - record['color']['deduct']
        record['large']['sum'] = record['large']['count'] - record['large']['invalid']

        # 正規化 張數為負數時
        record['black']['sum'] = record['black']['sum'] if record['black']['sum'] > 0 else 0
        record['color']['sum'] = record['color']['sum'] if record['color']['sum'] > 0 else 0
        record['large']['sum'] = record['large']['sum'] if record['large']['sum'] > 0 else 0
        _logger.info(f"date=> {record['date']['start']}/{record['date']['end']}")
        _logger.info(f"count=> {record['black']['count']}/{record['color']['count']}/{record['large']['count']}")
        _logger.info(f"deduct=> {record['black']['deduct']}/{record['color']['deduct']}/{record['large']['deduct']}")
        _logger.info(
            f"invalid=> {record['black']['invalid']}/{record['color']['invalid']}/{record['large']['invalid']}")
        _logger.info(f"sum=> {record['black']['sum']}/{record['color']['sum']}/{record['large']['sum']}")
        _logger.info(f'===== _calc_sheet end =====')
        return record

    # ==== Region:records, invalid, deduct ====

    # 記錄張數
    def _calc_records(self, _mfp_id, _meter_date, _stl_date):
        _logger.info(f"===== _calc_records start:{_mfp_id.name} =====")
        _logger.info(f"mfp_id=>{_mfp_id.name}")
        _logger.info(f"meter_date=>{_meter_date}")
        _logger.info(f"stl_date=>{_stl_date}")
        # ========== 抄表紀錄 ==========
        # 從抄表記錄獲取張數
        # 上次抄表日期: meter_date
        # 結算日: stl_date
        # 第一个条件 - 精确的日期和 mfp_id
        domain = ['|', '&',  # 条件1：精确匹配 _meter_date
                  ('date', '=', _meter_date),
                  ('mfp_id', '=', _mfp_id.id),
                  '&', '&',  # 条件2：日期范围匹配 _stl_date 前后 2 天
                  ('date', '>=', _stl_date - timedelta(days=2)),
                  ('date', '<=', _stl_date + timedelta(days=2)),
                  ('mfp_id', '=', _mfp_id.id)]
        # domain = ['&', '&',
        #           ('date', '>=', _meter_date),
        #           ('date', '<=', _stl_date),
        #           ('mfp_id', '=', _mfp_id.id)]
        records = self.env['mfp.record'].sudo().search(domain, order='date asc')
        _logger.info(f"len=>{len(records) if records else 0}")
        # 限制必須要兩筆以上的紀錄, 才可計算(後-前)
        if not records or len(records) < 2:
            return False
        start = True  # 此紀錄為起始紀錄
        _record = {
            'black': {'start': 0, 'end': 0, 'count': 0},
            'color': {'start': 0, 'end': 0, 'count': 0},
            'large': {'start': 0, 'end': 0, 'count': 0},
            'date': {'start': None, 'end': None},
            'description': None
        }

        for rec in records:
            if rec.state == '0' and start:
                # Initialize start values
                _record['black']['start'] = rec.black_print
                _record['color']['start'] = rec.color_print
                _record['large']['start'] = rec.large_print
                _record['date']['start'] = rec.date
                start = False
            elif rec.state in ['1', '3']:
                # Update start values and description
                _record['black']['start'] = rec.black_print
                _record['color']['start'] = rec.color_print
                _record['large']['start'] = rec.large_print
                _record['date']['start'] = rec.date
                _record['large']['description'] = '新機' if rec.state == '1' else '換機(新裝機)'
                start = False
            elif rec.state == '2':
                # Set end values and description, then break loop
                _record['black']['end'] = rec.black_print
                _record['color']['end'] = rec.color_print
                _record['large']['end'] = rec.large_print
                _record['date']['end'] = rec.date
                _record['large']['description'] = '退機'
                break
            elif rec.state == '4':
                pass
            else:
                # Update end values
                _record['black']['end'] = rec.black_print
                _record['color']['end'] = rec.color_print
                _record['large']['end'] = rec.large_print
                _record['date']['end'] = rec.date
        _record['black']['count'] = _record['black']['end'] - _record['black']['start']
        _record['color']['count'] = _record['color']['end'] - _record['color']['start']
        _record['large']['count'] = _record['large']['end'] - _record['large']['start']
        _logger.info(f"black=> {_record['black']['count']}/{_record['black']['start']}/{_record['black']['end']}")
        _logger.info(f"color=> {_record['color']['count']}/{_record['color']['start']}/{_record['color']['end']}")
        _logger.info(f"black=> {_record['large']['count']}/{_record['large']['start']}/{_record['large']['end']}")
        _logger.info(f"===== _calc_records end:{_mfp_id.name} =====")
        return _record

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

    # 贈送張數
    def _calc_deduct(self, _mfp_id):
        _record = {
            'black': {'deduct': _mfp_id.black_print_deduct},
            'color': {'deduct': _mfp_id.color_print_deduct},
            'large': {'deduct': 0},
        }
        return _record

    def merge_dicts(self, dicts):
        merged = defaultdict(dict)
        for d in dicts:
            for key, value in d.items():
                if key in merged:
                    # 合併現有鍵的值
                    merged[key].update(value)
                else:
                    merged[key] = value
        return dict(merged)

    # 合併三張(記錄,作廢,贈送)
    def _calc_printer(self, mfp_id, meter_date, stl_date):
        # 記錄張數
        records = self._calc_records(mfp_id, meter_date, stl_date)
        if not records or records['date']['end'] is None:
            return False
        deducts = self._calc_deduct(mfp_id)
        invalids = self._calc_invalid(mfp_id)
        # 合併三個字典
        record = self.merge_dicts([records, deducts, invalids])
        return record

    # 更新-事務機
    def _update_mfp_rental_date(self, mfp_id, date):
        _logger.info(f'_update_mfp_rental_date=>{mfp_id.name}->{date}')
        domain = [('id', '=', mfp_id.id)]
        mfp = self.env['mfp.data'].search(domain)
        mfp.update({'rental_date': date})

    def _update_mfp_meter_date(self, mfp_id, date):
        _logger.info(f'_update_mfp_meter_date=>{mfp_id.name}->{date}')
        domain = [('id', '=', mfp_id.id)]
        mfp = self.env['mfp.data'].search(domain)
        mfp.update({'meter_date': date})

    def _update_mfp_stl_date(self, mfp_id, date):
        _logger.info(f'_update_mfp_stl_date=>{mfp_id.name}->{date}')
        domain = [('id', '=', mfp_id.id)]
        mfp = self.env['mfp.data'].search(domain)
        mfp.update({'stl_date': date})

    # ==== End Region ====

    # ==== Region:account move ====
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

    # 增加商品明細-月租費
    def _cal_rentalprice(self, move_id, partner_id, date_start, date_end, rental_price, tax, is_adv):
        if rental_price > 0:
            # 產品ID: 影印費-基本月租費
            # adv_rental = 'mfp.product_product_mfp_adv_rental_price'
            # rental = 'mfp.product_product_mfp_rental_price'
            # ref_id = adv_rental if is_adv == '1' else rental
            ref_id = 'mfp.product_product_mfp_print_price'
            product_id = self.env.ref(ref_id)
            summary = f'{"預收 " if is_adv == "1" else ""}{date_start}~{date_end}'
            self._create_account_move_line(move_id, summary,
                                           partner_id, product_id, 1, rental_price, tax)

    # 增加商品明細-超印費
    def _cal_overprice(self, move_id, partner_id, date_start, date_end, over_price, tax, rental_price):
        # 超印
        if over_price > 0:
            # 產品ID: 超印費/影印費
            product_print_price = 'mfp.product_product_mfp_print_price'
            product_over_price = 'mfp.product_product_mfp_over_price'
            ref_id = product_over_price if rental_price > 0 else product_print_price
            product_id = self.env.ref(ref_id)
            summary = f'結算 {date_start}~{date_end}'
            self._create_account_move_line(move_id, summary,
                                           partner_id, product_id, 1, over_price, tax)

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
        # 稅金 5%(tw_tax_sale_5), 內含稅金 5%(tw_tax_sale_inc_5)
        tax_id = self.ref_id(tax)
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

    def _create_account_print_line(self, move_id, mfp_id, date_start, date_end, rental, period,
                                   black_print_start, black_print_end, black_print_invalid,
                                   color_print_start, color_print_end, color_print_invalid,
                                   large_print_start, large_print_end, large_print_invalid):
        value = {
            'move_id': move_id.id,
            'mfp_id': mfp_id.id,
            'date_start': date_start,
            'date_end': date_end,
            'rental': rental,
            'period': period,
            'black_print_start': black_print_start,
            'black_print_end': black_print_end,
            'black_print_invalid': black_print_invalid,
            'color_print_start': color_print_start,
            'color_print_end': color_print_end,
            'color_print_invalid': color_print_invalid,
            'large_print_start': large_print_start,
            'large_print_end': large_print_end,
            'large_print_invalid': large_print_invalid,
        }
        move_id.print_ids = [(0, 0, value)]

    # ==== End Region ====

    def _cal_printerline(self, move_id, mfp_id, date_start, date_end, period):
        records = self._calc_records(mfp_id, date_start, date_end)
        # if not records or records['date']['end'] is None:
        #     return False
        invalids = self._calc_invalid(mfp_id)
        rental = mfp_id.rental
        black_start = records['black']['start'] if records else False
        black_end = records['black']['end'] if records else False
        black_invalid = records['black']['invalid'] if records else False
        color_start = records['color']['start'] if records else False
        color_end = records['color']['end'] if records else False
        color_invalid = records['color']['invalid'] if records else False
        large_start = records['large']['start'] if records else False
        large_end = records['large']['end'] if records else False
        large_invalid = records['large']['invalid'] if records else False
        self._create_account_print_line(move_id, mfp_id, date_start, date_end, rental, period,
                                        black_start, black_end,
                                        black_invalid,
                                        color_start, color_end,
                                        color_invalid,
                                        large_start, large_end,
                                        large_invalid)

    def _calc_adv_rental(self, mfp_id):
        _logger.info(f"========== _calc_adv_rental start: ${mfp_id.name} ==========")
        # 若尚未到[結算日]則返回
        now = datetime.now().date()

        # ========== 發票(應收憑單)草稿 ==========
        # 客戶
        partner_id = mfp_id.company_id
        # 發票日期
        invoice_date = now
        # 含稅
        tax = mfp_id.tax
        if not tax:
            return False
        # # 會計
        # move_id = self._create_account_moves(invoice_date, partner_id)
        # 結算週期
        pay_period = int(mfp_id.pay_period)

        # ========== 發票明細行-月租費/預收月租 ==========
        # 月費
        rental = mfp_id.rental
        # 合併底下的月租
        merge_ids = mfp_id.merge_ids
        for mfp_merge in merge_ids:
            rental += mfp_merge.rental
        rental_price = rental * pay_period

        # 會計
        move_id = self._create_account_moves(invoice_date, partner_id)
        # ==== 月費結算 ====
        # 預繳
        is_adv = mfp_id.is_adv
        rental_date = mfp_id.rental_date
        while rental_date < now:
            # 結算月費起訖日
            rental_begin = rental_date
            rental_finish = rental_date + relativedelta(months=pay_period) + relativedelta(days=-1)
            # 月租/預收
            self._cal_rentalprice(move_id, partner_id, rental_begin, rental_finish, rental_price, tax, is_adv)

            rental_date = rental_date + relativedelta(months=pay_period)
            # 更新事務機月費資料
            self._update_mfp_rental_date(mfp_id, rental_date)
            for mfp_merge in merge_ids:
                self._update_mfp_rental_date(mfp_merge, rental_date)
        _logger.info(f"========== _calc_adv_rental end: ${mfp_id.name} ==========")
        return False

    def _calc_normal(self, mfp_id):
        _logger.info(f"========== _calc_normal start: ${mfp_id.name} ==========")
        # 若尚未到[結算日]則返回
        now = datetime.now().date()

        # ========== 發票(應收憑單)草稿 ==========
        # 客戶
        partner_id = mfp_id.company_id
        # 發票日期
        invoice_date = now
        # 含稅
        tax = mfp_id.tax
        if not tax:
            return False
        # # 會計
        # move_id = self._create_account_moves(invoice_date, partner_id)
        # 結算週期
        pay_period = int(mfp_id.pay_period)

        # ========== 發票明細行-月租費/預收月租 ==========
        # 月費
        rental = mfp_id.rental
        # 合併底下的月租
        merge_ids = mfp_id.merge_ids
        for mfp_merge in merge_ids:
            rental += mfp_merge.rental
        rental_price = rental * pay_period

        # ==== 月費結算 ====
        # 預繳
        is_adv = mfp_id.is_adv
        rental_date = mfp_id.rental_date
        # 會計
        move_id = self._create_account_moves(invoice_date, partner_id)

        while is_adv == '0' and rental_date < now:
            # 結算月費起訖日
            rental_begin = rental_date
            rental_finish = rental_date + relativedelta(months=pay_period) + relativedelta(days=-1)
            # 月租/預收
            self._cal_rentalprice(move_id, partner_id, rental_begin, rental_finish, rental_price, tax, is_adv)

            rental_date = rental_date + relativedelta(months=pay_period)
            # 更新事務機月費資料
            self._update_mfp_rental_date(mfp_id, rental_date)
            for mfp_merge in merge_ids:
                self._update_mfp_rental_date(mfp_merge, rental_date)
        # ==== 超印費結算 ====
        # 扣抵
        deduct = mfp_id.deduct
        stl_date = mfp_id.stl_date
        meter_date = mfp_id.meter_date
        while stl_date < now:
            # ========== 發票明細行-月租費/預收月租 ==========
            # 事務機(含合併)的月租&張數
            stl_begin = meter_date
            stl_finish = stl_date + relativedelta(months=pay_period) + relativedelta(days=-1)
            sheets = self._calc_sheet(mfp_id, stl_begin, stl_finish)
            # 明細顯示 日期範圍
            over_begin = stl_date
            over_finish = stl_date + relativedelta(months=pay_period) + relativedelta(days=-1)
            if not sheets:
                stl_date = stl_date + relativedelta(months=pay_period)
                # ========== 檢查 ==========
                # ==== 若日期較新,則更新「預收月租」日 ====
                self._update_mfp_stl_date(mfp_id, stl_date)
                for mfp_merge in merge_ids:
                    self._update_mfp_stl_date(mfp_merge, stl_date)

                # 事務機清單
                self._cal_printerline(move_id, mfp_id, over_begin, over_finish, pay_period)
                for mfp_merge in merge_ids:
                    self._cal_printerline(move_id, mfp_merge, over_begin, over_finish, pay_period)

                return False
            meter_date = sheets['date']['end']
            black_print = sheets['black']['sum']
            color_print = sheets['color']['sum']
            large_print = sheets['large']['sum']

            # 金額
            over_price = (mfp_id.black_print_overprice * black_print +
                          mfp_id.color_print_overprice * color_print +
                          mfp_id.large_print_overprice * large_print)

            # 扣抵
            over_price -= rental_price if deduct == '1' else 0
            # # 會計
            # move_id = self._create_account_moves(invoice_date, partner_id)
            # 超印
            self._cal_overprice(move_id, partner_id, over_begin, over_finish, over_price, tax, rental_price)

            stl_date = stl_date + relativedelta(months=pay_period)
            # ========== 檢查 ==========
            # ==== 若日期較新,則更新「預收月租」日 ====
            self._update_mfp_stl_date(mfp_id, stl_date)
            for mfp_merge in merge_ids:
                self._update_mfp_stl_date(mfp_merge, stl_date)

            # 事務機清單
            self._cal_printerline(move_id, mfp_id, over_begin, over_finish, pay_period)
            for mfp_merge in merge_ids:
                self._cal_printerline(move_id, mfp_merge, over_begin, over_finish, pay_period)

        # ========== 清除「作廢紀錄」 ==========
        invalid_ids = mfp_id.invalid_ids
        for rec in invalid_ids:
            rec.state = '1'

        for mfp_merge in merge_ids:
            invalid_ids = mfp_merge.invalid_ids
            for rec in invalid_ids:
                rec.state = '1'
        _logger.info(f"========== _calc_normal end: ${mfp_id.name} ==========")
        return False
