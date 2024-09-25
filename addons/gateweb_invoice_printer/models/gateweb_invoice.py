from odoo import fields, models, api


class GateWebInvoice(models.Model):
    _inherit = 'account.move'

    @api.depends('partner_id')
    def _compute_buyer(self):
        for record in self:
            buyer = record.partner_id
            record.buyer_identifier = buyer.invoice_vat if buyer.invoice_vat else buyer.vat
            record.buyer_name = buyer.invoice_name if buyer.invoice_name else buyer.name
