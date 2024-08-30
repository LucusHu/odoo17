import binascii
from odoo import _, http, fields
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.website_axis_helpdesk_advance.controller.portal_ticket import CustomerPortal


class ViewPortalHelpdesk(CustomerPortal):
    @http.route([
        "/axis/helpdesk/ticket/<int:ticket_id>/accept",
        "/axis/helpdesk/ticket/<int:ticket_id>/<access_token>/accept",
        '/axis/my/ticket/<int:ticket_id>/accept',
        '/axis/my/ticket/<int:ticket_id>/<access_token>/accept'
    ], type='json', auth="public", website=True)
    def portal_ticket_accept(self, ticket_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            ticket_sudo = self._document_check_access('axis.helpdesk.ticket', ticket_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid Ticket.')}

        try:
            ticket_sudo.write({
                'signature': signature,
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        query_string = f'/axis/my/ticket/{ticket_id}{"/" + access_token if access_token is not None else ""}?message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': query_string,
        }
