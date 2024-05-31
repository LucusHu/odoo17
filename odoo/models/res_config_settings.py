from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    client_id = fields.Char("Client ID")
    client_secret = fields.Char("Client Secret")
    redirect_uri = fields.Char("Redirect Uri")

    # redirect_uri = fields.Char("redirect uri", required=True)
    @api.model
    def get_values(self):
        config_parameter = self.env["ir.config_parameter"].sudo()
        res = super(ResConfigSettings, self).get_values()
        res["client_id"] = config_parameter.get_param("line.notify.client_id", default="")
        res["client_secret"] = config_parameter.get_param("line.notify.client_secret", default="")
        res["redirect_uri"] = config_parameter.get_param("line.notify.redirect_uri", default="")
        return res

    @api.model
    def set_values(self):
        config_parameter = self.env["ir.config_parameter"].sudo()
        # res = super(ResConfigSettings, self).set_values()
        config_parameter.set_param("line.notify.client_id", self.client_id)
        config_parameter.set_param("line.notify.client_secret", self.client_secret)
        config_parameter.set_param("line.notify.redirect_uri", self.redirect_uri)
