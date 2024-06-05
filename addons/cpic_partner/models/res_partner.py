from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # # 唯一值
    # _sql_constraints = [
    #     ('res_partner_vat', 'unique (vat, res_partner)', 'TaxID with the same name are unique per module.')
    # ]
    engineer_id = fields.Many2one("res.users", "負責工程師")
    fax = fields.Char("傳真")
    ext = fields.Char("分機")
    service_comment = fields.Char()
