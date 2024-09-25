from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    client_id = fields.Char("Client ID", required=True)
    client_secret = fields.Char("Client Secret", required=True)
    redirect_uri = fields.Char("Redirect Uri", required=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameter = self.env["ir.config_parameter"].sudo()
        res["client_id"] = config_parameter.get_param("line.notify.client_id")
        res["client_secret"] = config_parameter.get_param("line.notify.client_secret")
        res["redirect_uri"] = config_parameter.get_param("line.notify.redirect_uri")
        return res

    #
    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameter = self.env["ir.config_parameter"].sudo()
        config_parameter.set_param("line.notify.client_id", self.client_id)
        config_parameter.set_param("line.notify.client_secret", self.client_secret)
        config_parameter.set_param("line.notify.redirect_uri", self.redirect_uri)
