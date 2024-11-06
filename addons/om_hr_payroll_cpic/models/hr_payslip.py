from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        self.compute_sheet()
        return self.write({'state': 'done'})

    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                           self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            if not contract_ids:
                raise ValidationError(
                    _("No running contract found for the employee: %s or no contract in the given period" % payslip.employee_id.name))

            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})

            # ========== payslip extra ==========
            lines = [(0, 0, line) for line in self._get_payslip_extra_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})

        return True

    def _get_payslip_extra_lines(self, contract_ids, payslip_id):

        payslip = self.env['hr.payslip'].browse(payslip_id)
        contracts = self.env['hr.contract'].browse(contract_ids)

        domain = ['&', ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to)]
        payslip_extras = self.env['hr.payslip.extra'].search(domain)
        record = []
        for extra in payslip_extras:
            rule_id = extra.salary_rule_id
            value = {
                'salary_rule_id': rule_id.id,
                'contract_id': contracts[0].id,
                'name': rule_id.name,
                'code': rule_id.code,
                'category_id': rule_id.category_id.id,
                'sequence': rule_id.sequence,
                # 'appears_on_payslip': rule.appears_on_payslip,
                # 'condition_select': rule.condition_select,
                # 'condition_python': rule.condition_python,
                # 'condition_range': rule.condition_range,
                # 'condition_range_min': rule.condition_range_min,
                # 'condition_range_max': rule.condition_range_max,
                # 'amount_select': rule.amount_select,
                'amount_fix': rule_id.amount_fix,
                'amount_python_compute': rule_id.amount_python_compute,
                'amount_percentage': rule_id.amount_percentage,
                'amount_percentage_base': rule_id.amount_percentage_base,
                # 'register_id': rule.register_id.id,
                'amount': extra.amount,
                'employee_id': extra.employee_id.id,
                'quantity': extra.quantity,
                'rate': '100',
            }
            record.append(value)
        return record
