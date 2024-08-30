from odoo import fields, models, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(
        'x_Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        required=True,
        help="""Value of the product (automatically computed in AVCO).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")

    @api.model_create_multi
    def create(self, vals_list):
        self.action_confirm()
        # record = super().create(vals_list)
        # return record

    def action_confirm(self):
        # 返回一个前端动作，弹出确认框
        return {
            'type': 'ir.actions.client',
            'tag': 'action_confirm_dialog',
            'params': {
                'message': '你确定要执行此操作吗？',
            }
        }
