from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    phone = fields.Char('Phone', related='partner_id.phone')
    mobile = fields.Char('Mobile', related='partner_id.mobile')

    def action_cancel_btn(self):
        # self.picking_ids.filtered(lambda p: p.state != 'done').action_cancel()
        if not self.picking_ids:
            raise UserError("The specified picking record does not exist.")
        return_picking = self.env['stock.return.picking'].create({
            'picking_id': self.picking_ids.ids[0]
        })
        context = return_picking.create_returns()
        picking = self.env['stock.picking'].browse(context['res_id'])
        picking.button_validate()
        for invoice_id in self.invoice_ids:
            invoice_id.button_draft()
            invoice_id.button_cancel()

        return super()._action_cancel()

    # def _action_cancel(self):
    #     pass
