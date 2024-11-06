from datetime import date
from typing import Dict, List

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class PayslipExtra(models.Model):
    _name = 'hr.payslip.extra'

    category_id = fields.Many2one('hr.salary.rule.category', 'Category', required=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Rule', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)

    @api.onchange('salary_rule_id')
    def onchange_salary_rule_id(self):
        salary_rule_id = self.salary_rule_id
        self.code = salary_rule_id.code
        self.category_id = salary_rule_id.category_id

    name = fields.Char(required=True, translate=True)

    date = fields.Date('Date', required=True,
                       default=lambda self: fields.Date.to_string(date.today()))
    code = fields.Char(readonly=True,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                            "In that case, it is case sensitive.")

    # rate = fields.Float(string='Rate (%)', default=100.0)
    amount = fields.Float()
    quantity = fields.Float(default=1.0)
    total = fields.Float(compute='_compute_total', string='Total')

    @api.depends('quantity', 'amount')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount

    @api.model_create_multi
    def create(self, vals_list):
        return super(PayslipExtra, self).create(vals_list)
