# -*- coding: utf-8 -*-
from odoo import fields, models, api


# 公司: Comany's Structure
class ResPartner(models.Model):
    _inherit = 'res.partner'

    test_name = fields.Char()
    number = fields.Integer("設備數量", required=True, default=0)

