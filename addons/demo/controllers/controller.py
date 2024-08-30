import json
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import request


class Controller(http.Controller):

    @http.route(['/test/example'], type='json', auth="none", method=['POST'])
    def example(self):
        values = '測試成功'
        return json.dumps(values)