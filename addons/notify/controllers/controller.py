from odoo import http
from odoo.http import request


class Controller(http.Controller):

    @http.route(['/callback/example'], auth="none", method=['GET'])
    def example(self, **kwargs):
        return '成功'

    @http.route("/callback/notify", auth="none", methods=['GET'])
    def notify(self, code, state):
        referer = request.httprequest.headers.get('referer')
        if not (referer == 'https://notify-bot.line.me/'):
            return '來源錯誤 請重新檢查'

        if 'res_partner' in state:
            state = state.replace('res_partner', '')
            domain = [('id', '=', state)]
            partners = request.env['res.partner'].sudo().search(domain)
            if not partners:
                return '參數錯誤 請重新檢查'
            partners.update({'line_code': code})
            partners.get_token(code)
            return '恭喜完成 LINE Notify 連動！請關閉此視窗。'
        if 'res_user' in state:
            state = state.replace('res_user', '')
            domain = [('id', '=', state)]
            users = request.env['res.users'].sudo().search(domain)
            if not users:
                return '參數錯誤 請重新檢查'
            users.update({'line_code': code})
            users.get_token(code)
            return '恭喜完成 LINE Notify 連動！請關閉此視窗。'
        return '很可惜尚未參數錯誤 請重新檢查。'
