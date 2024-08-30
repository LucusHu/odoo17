odoo.define('website_axis_helpdesk_advance.portal_post', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var composer = require('portal.composer')

 $(document).ready(function() {
        $(".customer_rating").click(function(){

            var id = $(this).attr('data-value');
            document.getElementById('ticket_id').value = id;
            document.getElementById('ticketvalue_id').value = id;

        });
       });
});
