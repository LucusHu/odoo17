from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_vat = fields.Char('發票統編')
    invoice_name = fields.Char('發票抬頭')
