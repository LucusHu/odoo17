from odoo import fields, models, api


class Test(models.Model):
    _name = 'test'
    _description = 'Description'
    _check_company_auto = True

    name = fields.Char()
    company_id = fields.Many2one('res.company', '公司')
    company_number = fields.Char('公司編號', check_company=True)

    journal_id = fields.Many2one('account.journal', 'Journal',
                                 domain="[('company_id', '=', company_id), "
                                        "('type', '=', 'bank'), "
                                        "('bank_account_id', '=', False)]",
                                 required=True,
                                 check_company=True,
                                 tracking=True, )
    bank_journal_id = fields.Many2one("account.journal", "Bank Account",
                                      domain="[('company_id', '=', company_id), "
                                             "('type', '=', 'bank'), "
                                             "('bank_account_id', '!=', False)]",
                                      required=True,
                                      check_company=True,
                                      tracking=True, )
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  required=True,
                                  tracking=True, )

    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft', )
