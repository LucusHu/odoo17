# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'HelpDesk Ticket for Customer signature',
    'version': '14.0.0.1',
    'summary': 'Signature HelpDek Ticket Order',
    'description': 'Ticket Order Signature',
    'category': 'Tools',
    'author': 'JasonWu',
    'license': 'LGPL-3',
    'depends': ['portal', 'helpdesk_mgmt'],
    'data': [
        'views/helpdesk_ticket.xml',
        'views/helpdesk_ticket_signature_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
