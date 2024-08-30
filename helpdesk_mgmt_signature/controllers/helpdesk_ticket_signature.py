# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import binascii
from odoo import _, http, fields
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.helpdesk_mgmt.controllers.myaccount import CustomerPortalHelpdesk


class CustomerPortalHelpdesk(CustomerPortalHelpdesk):
    @http.route(
        ["/my/ticket/<int:ticket_id>"], type="http", auth="public", website=True
    )
    def portal_my_ticket(self, ticket_id=None, access_token=None, **kw):
        try:
            ticket_sudo = self._document_check_access(
                "helpdesk.ticket", ticket_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._ticket_get_page_view_values(ticket_sudo, access_token, **kw)
        return request.render("helpdesk_mgmt.portal_helpdesk_ticket_page", values)

    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        closed_stages = request.env["helpdesk.ticket.stage"].search(
            [("closed", "=", True)]
        )
        values = {
            'token': access_token,
            'ticket_id': ticket.id,
            # 'access_token': kwargs['hash'],
            "page_name": "ticket",
            "partner_name": ticket.partner_id.name,
            "ticket": ticket,
            "closed_stages": closed_stages,
        }

        if kwargs.get("error"):
            values["error"] = kwargs["error"]
        if kwargs.get("warning"):
            values["warning"] = kwargs["warning"]
        if kwargs.get("success"):
            values["success"] = kwargs["success"]

        return values

    @http.route(['/my/ticket/<int:ticket_id>/accept'], type='json', auth="public", website=True)
    def portal_ticket_accept(self, ticket_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            ticket_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token=access_token)
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

        # _message_post_helper(
        #     'helpdesk.ticket', ticket_sudo.id, _('Ticket signed by %s') % (name,),
        #     attachments=[('%s.pdf' % ticket_sudo.name, pdf)],
        #     **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'

        return {
            'force_refresh': True,
            'redirect_url': ticket_sudo.get_portal_url(query_string=query_string),
        }
