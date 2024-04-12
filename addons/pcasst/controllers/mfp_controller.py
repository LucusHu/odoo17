import json
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import request


class MFPController(http.Controller):

    @http.route(['/mfp/example'], type='json', auth="none", method=['POST'])
    def example(self):
        values = {}
        datas = request.env['res.partner'].sudo().search([])
        records = []
        if datas:
            values['records'] = records
            values['state'] = True
        else:
            values['records'] = ''
            values['state'] = False
        return json.dumps(values)

    @http.route('/mfp/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        return request.session

    # 驗證-帳號密碼
    @http.route(['/mfp/authorization'], type='json', auth="none", method=['POST'])
    def authorization(self, account, password):
        domain = ['&', '&',
                  ('parent_id', '!=', False),
                  ('account', '=', account),
                  ('password', '=', password)]
        res_partner = request.env['res.partner'].sudo().search(domain)
        records = []
        for item in res_partner:
            records.append({
                'company_id': item.parent_id.id if item.parent_id else '',
                'id': item.id,
                'name': item.name,
                'mobile': item.mobile,
            })
        return records

    @http.route(['/mfp/company'], type='json', auth="none", method=['POST'])
    def company_data(self, keyword=None):
        domain = [('parent_id', '=', False)]
        if keyword:
            domain = ['&',
                      ('parent_id', '=', False),
                      '|', ('name', 'ilike', keyword),
                      ('number', 'ilike', keyword)]
        res_partner = request.env['res.partner'].sudo().search(domain)
        records = []
        for item in res_partner:
            records.append({
                'id': item.id,
                'name': item.name,
                'number': item.number if item.number else '',
            })
        return records

    @http.route(['/mfp/place'], type='json', auth="none", method=['POST'])
    def place_data(self, company_id):
        domain = [('company_id', '=', company_id)]
        place_data = request.env['place.data'].sudo().search(domain)
        records = []
        for item in place_data:
            records.append({
                'id': item.id,
                'name': item.name,
                'install_place': item.install_place if item.install_place else '',
            })
        return records

    # 公司-維護工程師
    @http.route(['/mfp/staff'], type='json', auth="none", method=['POST'])
    def staff_data(self):
        domain = [('parent_id', '=', 1)]
        res_partner = request.env['res.partner'].sudo().search(domain)
        records = []
        for item in res_partner:
            records.append({
                'id': item.id,
                'name': item.name,
                'mobile': item.mobile,
            })
        return records

    @http.route(['/mfp/staff/update'], type='json', auth="none", method=['POST'])
    def staff_update(self, name, mobile, line, email):
        odoo = request.env['res.partner']

        domain = ['&',
                  ('parent_id', '=', 1),
                  ('mobile', '=', mobile)]
        res_partner = odoo.sudo().search(domain, limit=1)
        if not res_partner:
            res_partner = odoo.sudo().create({
                'parent_id': 1,
                'name': name,
                'mobile': mobile,
                'line': line,
                'email': email,
            })
        else:
            res_partner.update({
                'line': line
            })
        records = [{'id': res_partner.id}]
        return records

    # 公司-使用者
    @http.route(['/mfp/user'], type='json', auth="none", method=['POST'])
    def user_data(self, vat):
        odoo = request.env['res.partner']

        domain = [('vat', '=', vat)]
        parent_id = odoo.sudo().search(domain)

        domain = [('parent_id', '=', parent_id.id)]
        res_partner = request.env['res.partner'].sudo().search(domain)
        records = []
        for item in res_partner:
            records.append({
                'id': item.id,
                'name': item.name,
                'mobile': item.mobile,
            })
        return records

    @http.route(['/mfp/user/update'], type='json', auth="none", method=['POST'])
    def user_update(self, vat, name, mobile, line, email):
        odoo = request.env['res.partner']

        domain = [('vat', '=', vat)]
        parent_id = odoo.sudo().search(domain, limit=1)

        domain = ['&',
                  ('parent_id', '=', parent_id.id),
                  ('mobile', '=', mobile)]
        res_partner = odoo.sudo().search(domain, limit=1)
        if not res_partner or (len(res_partner) == 0):
            value = {
                'company_type': 'company',
                'is_company': False,
                'parent_id': parent_id.id,
                'name': name,
                'mobile': mobile,
                'line': line,
                'email': email,
            }
            res_partner = odoo.sudo().create(value)
        else:
            res_partner.update({
                'line': line,
                'email': email,
            })
        records = [{'id': res_partner.id}]
        return records

    # 事務機-品牌
    @http.route(['/mfp/brand'], type='json', auth="none", method=['POST'])
    def brand_data(self):
        domain = []
        brand_data = request.env['brand.data'].sudo().search(domain)
        records = []
        for item in brand_data:
            records.append({
                'id': item.id,
                'name': item.name,
            })
        return records

    # 事務機-型號
    @http.route(['/mfp/model'], type='json', auth="none", method=['POST'])
    def model_data(self, brand_id):
        domain = [('brand_id', '=', brand_id)]
        model_data = request.env['model.data'].sudo().search(domain)
        records = []
        for item in model_data:
            records.append({
                'id': item.id,
                'name': item.name,
            })
        return records

    # 事務機-資料
    @http.route(['/mfp/mfp'], type='json', auth="none", method=['POST'])
    def mfp_data(self, company_id=None, place_id=None, user_id=None):
        domain = [('state', '!=', '2')]
        if company_id:
            domain.append(('company_id', '=', company_id))
        elif place_id:
            domain.append(('place_id', '=', place_id))
        elif user_id:
            domain.append(('user_id', '=', user_id))
        length = len(domain)
        for i in range(length):
            if i == 0:
                continue
            domain = ['&'] + domain
        mfp_data = request.env['mfp.data'].sudo().search(domain)
        records = []
        for item in mfp_data:
            records.append({
                'company_id': item.company_id.id if item.company_id else '',
                'place_id': item.place_id.id if item.place_id else '',
                'user_id': item.user_id.id if item.user_id else '',
                'model_id': item.model_id.code if item.model_id else '',
                'id': item.id,
                'name': item.name,
                'description': item.description if item.description else '',
                'state': item.state,
                'number': item.company_number if item.company_number else '',
                'serial_number': item.serial_number if item.serial_number else '',
                'ip': item.ip if item.ip else '',
                'status': item.status,
                'contract_start': item.contract_start,
                'contract_end': item.contract_end,
                'contract_model': item.contract_model,
                'deposit': item.deposit,
                'meter_day': item.meter_day,
                'rental': item.rental,
                'pay_period': item.pay_period,
                'black_print_overprice': item.black_print_overprice,
                'black_print_deduct': item.black_print_deduct,
                'color_print_overprice': item.color_print_overprice,
                'color_print_deduct': item.color_print_deduct,
                'large_print_overprice': item.large_print_overprice,
            })
        return records

    @http.route(['/mfp/mfp/update'], type='json', auth="none", method=['POST'])
    def mfp_update(self, mfp_id, ip, serial_number, status, instead_mfp):
        # 查詢事務機
        domain = [('id', '=', mfp_id)]
        mfp_data = request.env['mfp.data'].sudo().search(domain)
        mfp_data.update({
            'serial_number': serial_number,
            'ip': ip,
            'status': str(status),
            'state': '2' if status == 2 else '1',
        })
        domain = [('id', '=', instead_mfp)]
        instead_mfp = request.env['mfp.data'].sudo().search(domain)
        if instead_mfp:
            mfp_data.update({
                'mfp_records': [(4, instead_mfp.id, 0)],
            })
        records = [{'id': mfp_data.id}]
        return records

    @http.route(['/mfp/mfp/supplies'], type='json', auth="none", method=['POST'])
    def mfp_supplies(self, mfp_id,
                     toner_black, toner_cyan, toner_magenta, toner_yellow, toner_waste,
                     drum_black, drum_cyan, drum_magenta, drum_yellow):
        # 查詢事務機
        domain = [('id', '=', mfp_id)]
        mfp_data = request.env['mfp.data'].sudo().search(domain)
        mfp_data.update({
            'toner_black': float(toner_black),
            'toner_cyan': float(toner_cyan),
            'toner_magenta': float(toner_magenta),
            'toner_yellow': float(toner_yellow),
            'toner_waste': float(toner_waste),
            'drum_black': float(drum_black),
            'drum_cyan': float(drum_cyan),
            'drum_magenta': float(drum_magenta),
            'drum_yellow': float(drum_yellow),
        })
        records = [{'id': mfp_data.id}]
        return records

    # 事務機-固定週期(預計每月30日)
    @http.route(['/mfp/mfp/period'], type='json', auth="none", method=['POST'])
    def mfp_period(self, company_id=None, place_id=None):
        domain = [('state', '!=', '2')]
        if company_id:
            domain.append(('company_id', '=', company_id))
        elif place_id:
            domain.append(('place_id', '=', place_id))
        length = len(domain)
        for i in range(length):
            if i == 0:
                continue
            domain = ['&'] + domain
        mfp_data = request.env['mfp.data'].sudo().search(domain)

        records = []
        # ========== 計算日期 ==========
        date = datetime.now().date()
        time = datetime.now().time()
        # next_month = datetime(now.year, now.month, 1) + relativedelta(months=1)
        # # 當月最後一天是幾號
        # current_month = next_month - timedelta(days=1)
        # current_days = current_month.day

        for item in mfp_data:
            counter = False
            # ========== 計算優先順序 ==========
            priority = 0
            for i in range(item.meter_before, -item.meter_after):
                if item.next_period == (date + timedelta(days=i)) and 10 <= time.hour <= 16:
                    # 是否已存在紀錄
                    domain = ['&',
                              ('id', '=', item.id),
                              ('date', '=', date)]
                    mfp_records = request.env['mfp.record'].sudo().search(domain)
                    counter = False if mfp_records else True
                    # 優先順序
                    priority = i if (i == 0) else ((-i + 1) if (i < 0) else (i + item.meter_after))
                    break
            # -2, -1 => 2, 1 => (+2) 4, 3
            # priority = -priority + item.meter_before if priority < 0 else priority
            # 1, 2
            # priority = priority if priority > 0 else priority
            # 0 => 1
            # priority = priority + 1

            # ========== 紀錄 ==========
            records.append({
                'company_id': item.company_id.id if item.company_id else '',
                'place_id': item.place_id.id if item.place_id else '',
                'user_id': item.user_id.id if item.user_id else '',
                'model_id': item.model_id.id if item.model_id else '',
                'id': item.id,
                'name': item.name,
                'description': item.description if item.description else '',
                'number': item.company_number if item.company_number else '',
                'serial_number': item.serial_number if item.serial_number else '',
                'ip': item.ip if item.ip else '',
                'contract_start': item.contract_start,
                'contract_end': item.contract_end,
                'contract_model': item.contract_model,
                'deposit': item.deposit,
                'meter_day': item.meter_day,
                'rental': item.rental,
                'pay_period': item.pay_period,
                # 'overprint_pay_period': item.overprint_pay_period,
                # 'black_print_overprice': item.black_print_overprice,
                # 'black_print_deduct': item.black_print_deduct,
                # 'color_print_overprice': item.color_print_overprice,
                # 'color_print_deduct': item.color_print_deduct,
                # 'large_print_overprice': item.large_print_overprice,
                'counter': counter,
                'priority': priority,
                'date_start': item.next_period - timedelta(days=item.meter_before),
                'date_end': item.next_period + timedelta(days=item.meter_after),
            })
        return records

    @http.route(['/mfp/mfp_record'], type='json', auth="none", method=['POST'])
    def mfp_record(self, mfp_id):
        domain = [('mfp_id', '=', mfp_id)]
        mfp_record = request.env['mfp.record'].sudo().search(domain)
        records = []
        for item in mfp_record:
            records.append({
                'company_id': item.company_id.id if item.company_id else '',
                'place_id': item.place_id.id if item.place_id else '',
                'user_id': item.user_id.id if item.user_id else '',
                'id': item.id,
                'black_print': item.black_print,
                'color_print': item.color_print,
                'large_print': item.large_print,
                'date': item.date,
                'print_status': item.print_status,
            })
        return records

    def get_record_id_by_external_id(self, external_id):
        # 使用search方法查找外部ID
        ir_model_data = request.env['ir.model.data'].sudo().search([('name', '=', external_id)])
        # 如果找到，取得相對應的記錄ID
        # 如果找不到，返回None或者其他適當的值
        return ir_model_data.res_id if ir_model_data else False

    @http.route(['/mfp/mfp_record/write'], type='json', auth="none", method=['POST'])
    def mfp_record_write(self, mfp_id, date, black_print, color_print, large_print, print_status):
        # 查詢事務機
        if not black_print and not color_print and not large_print and str(print_status) == '0':
            return []
        domain = [('id', '=', mfp_id)]
        mfp_datas = request.env['mfp.data'].sudo().search(domain)

        # 建立/更新 mfp record
        value = {
            'company_id': mfp_datas.company_id.id,
            'place_id': mfp_datas.place_id.id,
            'mfp_id': mfp_datas.id,
            'user_id': mfp_datas.user_id.id,
            'date': date,
            'black_print': black_print,
            'color_print': color_print,
            'large_print': large_print,
            'print_status': str(print_status),
            'category_id': [(6, 0, [self.get_record_id_by_external_id('mfp_record_category_auto')])]
        }
        domain = ['&', '&',
                  ('mfp_id', '=', mfp_datas.id),
                  ('date', '=', date),
                  ('print_status', '=', str(print_status))]
        mfp_record = request.env['mfp.record'].sudo().search(domain, limit=1)
        if mfp_record:
            mfp_record.update(value)
            mfp_record.count = mfp_record.count + 1
            record = mfp_record
        else:
            record = request.env['mfp.record'].sudo().create(value)
        records = [{'id': record.id}]
        return records

    @http.route(['/mfp/install_record/write'], type='json', auth="none", method=['POST'])
    def install_record_write(self, mfp_id, date, user_id, name, install_place, install_status):
        # 查詢事務機
        domain = [('id', '=', mfp_id)]
        mfp_datas = request.env['mfp.data'].sudo().search(domain)
        # 查詢裝機地點
        domain = [('id', '=', mfp_datas.place_id.id)]
        place_datas = request.env['place.data'].sudo().search(domain)
        place_datas.write({'install_place': install_place})

        domain = [('mfp_id', '=', mfp_datas.id)]
        install_record = request.env['install.record'].sudo().search(domain, limit=1)
        value = {
            'company_id': mfp_datas.company_id.id,
            'place_id': mfp_datas.place_id.id,
            'mfp_id': mfp_datas.id,
            'user_id': user_id,
            'name': name,
            'date': date,
            'install_place': install_place,
            'install_status': str(install_status),
        }
        if install_record:
            install_record.update(value)
            install_record.count = install_record.count + 1
            record = install_record
        else:
            record = install_record.sudo().create(value)
        records = [{'id': record.id}]
        return records

    @http.route(['/mfp/account_move/write'], type='json', auth="none", method=['POST'])
    def account_move_write(self, mfp_id):
        # 查詢事務機
        domain = [('id', '=', mfp_id)]
        mfp_data = request.env['mfp.data'].sudo().search(domain)
        records = []
        account_move = mfp_data.printer_pay(mfp_data)
        if account_move:
            records.append({'id': account_move.id})
        return records

    @http.route(['/mfp/account_move/trigger'], type='json', auth="none", method=['POST'])
    def account_move_trigger(self):
        # 查詢事務機
        request.env['mfp.data'].sudo().iron_account()
        request.env['mfp.data'].sudo().iron_noreocrd()

    @http.route(['/mfp/line_record'], type='json', auth="none", method=['POST'])
    def line_record(self):
        domain = [('status', '=', '0')]
        line_records = request.env['line.record'].sudo().search(domain)
        records = []
        for line in line_records:
            records.append({
                'id': line.id,
                'line': line.line,
                'message': line.message,
            })
        return records

    @http.route(['/mfp/line_record/write'], type='json', auth="none", method=['POST'])
    def line_record_write(self, line_id, status, error):
        domain = [('id', '=', line_id)]
        line_records = request.env['line.record'].sudo().search(domain)
        records = []
        if line_records:
            line_records.update({
                'status': str(status),
                'error': error,
            })
            records = [{'id': line_records.id}]
        return records
