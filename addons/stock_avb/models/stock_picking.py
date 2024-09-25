from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_btn(self):
        # move_ids, move_line_ids,
        # 退貨: return_ids,
        # 採購: purchase_id,
        # 接收: picking_type_code: 'incoming'/'outgoing'

        # §move_line:
        # 序號: lot_name
        for rec in self:
            for line in rec.return_ids:
                _rec = {
                    'id': line.id,
                }
            for line in rec.move_line_ids:
                _rec = {
                    'id': line.id,
                    'product_id': line.product_id,
                    'lot_id': line.lot_id,
                }
            value = {
                'move_ids': rec.move_ids,
                'move_line_ids': rec.move_line_ids,
                'return_ids': rec.return_ids,
                'purchase_id': rec.purchase_id,
                'sale_id': rec.sale_id,
                'purchase_id.partner_id': rec.purchase_id.partner_id,
                'picking_type_code': rec.picking_type_code,
            }
            pass
