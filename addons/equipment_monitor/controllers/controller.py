import json
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import request


class Controller(http.Controller):

    @http.route(['/equipment_monitor/example'], type='json', auth="none", method=['POST'])
    def example(self):
        values = {}
        datas = request.env['res.partner'].sudo().search([])
        records = []
        if datas:
            values['records'] = records
            values['state'] = True
        else:
            values['records'] = ''
            values['state'] = False
        return json.dumps(values)