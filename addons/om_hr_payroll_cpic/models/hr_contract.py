from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    accident_insurance = fields.Monetary('Labor Insurance', help='Accident Insurance')
    accident_insurance_contributed = fields.Float('Labor Ins. Contributed')
    health_insurance = fields.Monetary('Health Insurance', help='Health Insurance')
    health_insurance_dependents = fields.Integer('Health Ins. Dependents')
