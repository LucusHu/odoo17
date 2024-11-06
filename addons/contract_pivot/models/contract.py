from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    # category_ids = fields.Many2many('contract.tag.category', string='Category')
    category_id = fields.Many2one('contract.tag.category', string='Category')

    unit_price = fields.Float('Unit Price', compute='_compute_unit_price', store=True, help='unit price=price/month')

    # 計算每月單價: 每月金額=總金額/每月
    @api.depends('recurring_interval', 'recurring_rule_type', 'contract_line_fixed_ids')
    def _compute_unit_price(self):
        for record in self:
            rule_type = record.recurring_rule_type
            interval = record.recurring_interval
            line_ids = record.contract_line_fixed_ids
            if not rule_type or not interval or not line_ids:
                record.unit_price = 0
                continue
            amount = 0
            for line in line_ids:
                amount += line.price_subtotal
            month = 1
            if rule_type == 'daily':
                month = interval / 30
            elif rule_type == 'weekly':
                month = interval / 4
            elif rule_type == 'monthly' or rule_type == 'monthlylastday':
                month = interval
            elif rule_type == 'quarterly':
                month = interval * 3
            elif rule_type == 'semesterly':
                month = interval * 6
            elif rule_type == 'yearly':
                month = interval * 12
            record.unit_price = amount / month

    specification = fields.Html('Specification')
