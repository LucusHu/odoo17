from odoo import fields, models, api


class GateWebInvoice(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_buyer(self):
        buyer = self.partner_id
        self.buyer_identifier = buyer.invoice_vat if buyer.invoice_vat else buyer.vat
        self.buyer_name = buyer.invoice_name if buyer.invoice_name else buyer.name
