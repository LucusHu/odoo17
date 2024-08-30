from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'number'

    place_ids = fields.One2many('mfp.place', 'company_id')

    code = fields.Char(string='Code', readonly=True)
    number = fields.Char('客戶編號')
    fax = fields.Char('傳真')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'code' not in vals or not vals['code']:
                # 沒有代碼，給予一個新代碼
                vals['code'] = self.env['ir.sequence'].next_by_code('mfp.company.sequence')
                vals['code'] = self.env['ir.sequence'].next_by_code('mfp.company.sequence')
                while True:
                    domain = [('code', '=', vals['code'])]
                    partners = self.env['res.partner'].search(domain)
                    if len(partners) == 0:
                        break
                    vals['code'] = self.env['ir.sequence'].next_by_code('mfp.company.sequence')
        return super(ResPartner, self).create(vals_list)

    # 自動針對聯絡人給予Code碼
    def check_and_update_code(self):
        partners = self.search([])
        for partner in partners:
            if not partner.code:
                partner.code = self.env['ir.sequence'].next_by_code('mfp.company.sequence') or 'DefaultCode'
