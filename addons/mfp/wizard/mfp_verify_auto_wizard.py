from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MFPVerifyAutoWizard(models.TransientModel):
    _name = 'mfp.verify.auto.wizard'
    _description = 'MFP自動驗證'

    def verify_start(self):
        _logger.info(f"========== verify start: {datetime.now()} ==========")
        _logger.info(f"===== create company & place start: =====")
        name = '測試公司'
        partner = self.env['res.partner'].sudo().search([('name', '=', name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].sudo().create({
                'name': name,
                'vat': '123456789',
                'number': 'T1234',
            })
        if not partner:
            raise UserError('聯絡人(公司),「基本資料」異常')

        place = self.env['mfp.place'].sudo().search([('company_id', '=', partner.id)], limit=1)
        if not place:
            name = f'{partner.name}-辦公室'
            place = self.env['mfp.place'].sudo().create({
                'company_id': partner.id,
                'name': name
            })
        if not place:
            raise UserError('聯絡人(公司),「裝置地點」異常')
        _logger.info(f"===== create company & place end: =====")
        _logger.info(f"===== create mfp start: =====")
        name = '事務機(測試)'
        mfp = self.env['mfp.data'].sudo().search(['&', '&',
                                                  ('company_id', '=', partner.id),
                                                  ('place_id', '=', place.id),
                                                  ('name', '=', name)], limit=1)
        if not mfp:
            name = f'{partner.name}-辦公室'
            brand_id = self.env.ref('mfp.mfp_brand_ricoh')
            model_id = self.env.ref('mfp.mfp_model_ricoh_c5503')
            mfp = self.env['mfp.data'].sudo().create({
                'company_id': partner.id,
                'place_id': place.id,
                'name': name,
                'brand_id': brand_id.id,
                'model_id': model_id.id,
                'black_print_overprice': 0.4,
                'color_print_overprice': 4,
                'large_print_overprice': 10,
            })
        if not mfp:
            raise UserError('事務機,「基本資料」異常')
        # 获取当前日期
        today = fields.Date.today()
        # 计算三个月前的日期
        one_months_ago = today - relativedelta(months=1)
        two_months_ago = today - relativedelta(months=2)
        three_months_ago = today - relativedelta(months=3)

        mfp_record = self.env['mfp.record'].sudo().search(['&', '&',
                                                           ('mfp_id', '=', mfp.id),
                                                           ('date', '>=', three_months_ago),
                                                           ('date', '<=', today)])
        if len(mfp_record) < 3:
            values = [
                {
                    'mfp_id': mfp.id,
                    'date': three_months_ago,
                    'black_print': 0,
                    'color_print': 0,
                    'large_print': 0,
                },
                {
                    'mfp_id': mfp.id,
                    'date': two_months_ago,  # 当前日期
                    'black_print': 1000,
                    'color_print': 500,
                    'large_print': 10,
                },
                {
                    'mfp_id': mfp.id,
                    'date': one_months_ago,  # 其他日期
                    'black_print': 2000,
                    'color_print': 1000,
                    'large_print': 20,
                }
            ]
            self.env['mfp.record'].sudo().create(values)
        _logger.info(f"===== create mfp end: =====")
        _logger.info(f"========== verify end: {datetime.now()} ==========")
        pass
