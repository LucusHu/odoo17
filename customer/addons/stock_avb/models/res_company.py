from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    fax = fields.Char('傳真')

    def get_address(self):
        self.ensure_one()
        company = self
        return ('%s%s%s%s' % (
            company.state_id.name if company.state_id else '',
            company.city if company.city else '',
            company.street if company.street else '',
            company.street2 if company.street2 else '',))
