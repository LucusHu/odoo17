from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fax = fields.Char('傳真')

    def get_address(self):
        self.ensure_one()
        partner = self
        return ('%s%s%s%s' % (
            partner.state_id.name if partner.state_id else '',
            partner.city if partner.city else '',
            partner.street if partner.street else '',
            partner.street2 if partner.street2 else '',))

    def get_contact(self):
        self.ensure_one()
        for partner in self.child_ids:
            return partner.name
