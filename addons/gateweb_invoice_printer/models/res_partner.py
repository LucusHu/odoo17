from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_vat = fields.Char('開立發票統編', help='若有填寫則取代原始發票統編')
    invoice_name = fields.Char('開立發票抬頭', help='若有填寫則取代原始發票抬頭')
