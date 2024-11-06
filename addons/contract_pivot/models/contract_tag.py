from odoo import fields, models


# class ContractTagPayment(models.Model):
#     _name = "contract.tag.payment"
#     _description = "Contract Tag Payment"
#
#     name = fields.Char(required=True)
#     company_id = fields.Many2one(
#         "res.company",
#         string="Company",
#         default=lambda self: self.env.company.id,
#     )
#     color = fields.Integer("Color Index", default=0)


class ContractTagCategory(models.Model):
    _name = "contract.tag.category"
    _description = "Contract Tags of Category"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company.id,
    )
    color = fields.Integer("Color Index", default=0)
