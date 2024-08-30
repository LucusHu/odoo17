from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo import http
from odoo.http import request


class ViewPortalHelpdesk(CustomerPortal):

    @http.route(['/axis/helpdesk/rating/submit'], type='http', auth="public", website=True)
    def index_submit(self, access_token=None, **post):
        ticket_id = post.get('id')
        rating = post.get('rating')
        comment = post.get('comment')
        ticket = request.env['axis.helpdesk.ticket'].sudo().search([('id', '=', ticket_id)])
        if rating == 'poor':
            ticket.priority_new = '1'
        if rating == 'average':
            ticket.priority_new = '2'
        if rating == 'good':
            ticket.priority_new = '3'
        if rating == 'excellent':
            ticket.priority_new = '4'
        if comment:
            ticket.write({'comment': comment})

        return request.render('website_axis_helpdesk_advance.rating_submit')
