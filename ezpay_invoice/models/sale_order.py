# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EzpayInvoiceSaleOrder(models.Model):
    _inherit = 'sale.order'

    ez_print = fields.Boolean(string="列印")
    ez_donate = fields.Boolean(string="捐贈")
    ez_donate_number = fields.Char(string="愛心碼")
    ez_print_address = fields.Char(string="發票寄送地址")
    ez_ident_name = fields.Char(string="發票抬頭")
    ez_ident = fields.Char(string="統一編號")
    ez_carruer_type = fields.Selection(string='載具類別', selection=[('1', '綠界科技電子發票載具'), ('2', '消費者自然人憑證'),
                                                                 ('3', '消費者手機條碼')])
    ez_carruer_number = fields.Char(string="載具號碼")

    def _prepare_invoice(self):
        res = super(EzpayInvoiceSaleOrder, self)._prepare_invoice()

        res['ezpay_CustomerIdentifier'] = self.ez_ident
        res['is_print'] = self.ez_print
        res['is_donation'] = self.ez_donate
        res['lovecode'] = self.ez_donate_number
        res['ez_print_address'] = self.ez_print_address
        res['ez_ident_name'] = self.ez_ident_name
        res['carruerType'] = self.ez_carruer_type
        res['carruernum'] = self.ez_carruer_number

        return res
