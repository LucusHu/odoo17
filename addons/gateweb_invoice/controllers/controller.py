import json
from odoo import http


class Controller(http.Controller):

    @http.route(['/gateweb/example'], type='json', auth="none", method=['POST'])
    def example(self):
        values = '測試成功'
        return json.dumps(values)