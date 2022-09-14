# -*- coding: utf-8 -*-

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        sale_agreement = request.env['sale.agreement'].sudo()
        # if 'order_count' in counters:
        values['agreement_count'] = sale_agreement.search_count(self._prepare_agreements_domain(partner)) \
            if sale_agreement.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_agreements_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'ongoing',  'done'])
        ]

    # Sale Agreements
    def _get_agreement_searchbar_sortings(self):
        return {
            'date': {'label': _('Agreement Start Date'), 'order': 'planned_date_begin desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

    @http.route(['/my/agreements', '/my/agreements/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_agreements(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        sale_agreement = request.env['sale.agreement'].sudo()

        domain = self._prepare_agreements_domain(partner)

        searchbar_sortings = self._get_agreement_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        agreement_count = sale_agreement.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/agreements",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=agreement_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        agreements = sale_agreement.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_agreements_history'] = agreements.ids[:100]

        values.update({
            'date': date_begin,
            'agreements': agreements.sudo(),
            'page_name': 'agreement',
            'pager': pager,
            'default_url': '/my/agreements',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sd_sale_agreement.portal_my_agreements", values)

    @http.route(['/my/agreement/<int:agreement_id>'], type='http', auth="public", website=True)
    def portal_agreement_page(self, agreement_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            agreement_sudo = self._document_check_access('sale.agreement', agreement_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            if agreement_sudo and agreement_sudo.report_type_portal == 'normal':
                return self._show_report(model=agreement_sudo, report_type=report_type, report_ref='sd_sale_agreement.action_report_sale_agreement_without_quot', download=download)
            else:
                return self._show_report(model=agreement_sudo, report_type=report_type, report_ref='sd_sale_agreement.action_report_sale_agreement', download=download)

        # use sudo to allow accessing/viewing agreements for public user
        # only if he knows the private token
        # Log only once a day
        if agreement_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_agreement_%s' % agreement_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_agreement_%s' % agreement_sudo.id] = now
                body = _('Agreement viewed by customer %s', agreement_sudo.partner_id.name)
                _message_post_helper(
                    "sale.agreement",
                    agreement_sudo.id,
                    body,
                    token=agreement_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=agreement_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            'sale_agreement': agreement_sudo,
            'message': message,
            'token': access_token,
            'landing_route': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': agreement_sudo.partner_id.id,
            'report_type': 'html',
            'action': agreement_sudo._get_return_portal_action(),
        }

        history = request.session.get('my_agreements_history', [])
        values.update(get_records_pager(history, agreement_sudo))

        return request.render('sd_sale_agreement.agreement_portal_template', values)
