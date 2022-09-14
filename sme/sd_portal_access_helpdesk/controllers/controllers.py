# -*- coding: utf-8 -*-

from odoo.http import request
from operator import itemgetter
from markupsafe import Markup
from odoo import fields, http, SUPERUSER_ID, _
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
# from odoo.addons.portal.controllers import portal
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR, AND


class CustomerPortalInheritInvoice(CustomerPortal):
    """Inherit to overwrite the access right of sale/quotation on portal"""

    def _prepare_portal_layout_values(self):
        """To enable or disable the access on portal"""
        values = super(CustomerPortalInheritInvoice, self)._prepare_portal_layout_values()
        values['ticket_enable'] = False
        user_id = request.env['res.users'].browse(request.uid)
        partner_id = request.env['res.partner'].search([('user_ids', '=', user_id.id)], limit=1)
        if partner_id and partner_id.enable_helpdesk_portal_access:
            values['ticket_enable'] = True

        return values

    def custom_helpdesk_domain(self):
        partner = request.env.user.partner_id
        domain = []
        if partner.enable_helpdesk_portal_access and not partner.access_all_helpdesk_records:

            domain.append(('partner_id', '=', partner.id))
        if partner.access_follower_helpdesk_records and not partner.access_all_helpdesk_records:
            domain.insert(0,'|')
            domain.append(('message_follower_ids.partner_id', '=', partner.id))
        if partner.access_all_helpdesk_records and partner.access_follower_helpdesk_records:

            domain.append(('message_follower_ids.partner_id', '=', partner.id))
            if partner.child_ids:
                domain.insert(0, '|')
                domain.append(('partner_id', 'in', partner.child_ids.ids))
            if partner.parent_id:
                domain.insert(0, '|')
                domain.insert(0, '|')
                domain.append(('partner_id', 'child_of', partner.parent_id.id))
                domain.append(('partner_id', '=', partner.parent_id.id))

        if partner.access_all_helpdesk_records and not partner.access_follower_helpdesk_records:

            domain.append(('partner_id', '=', partner.id))
            if partner.child_ids:
                domain.insert(0, '|')
                domain.append(('partner_id', 'in', partner.child_ids.ids))
            if partner.parent_id:
                domain.insert(0, '|')
                domain.insert(0, '|')
                domain.append(('partner_id', 'child_of', partner.parent_id.id))
                domain.append(('partner_id', '=', partner.parent_id.id))

        return domain

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'ticket_count' in counters:
            domain = self._prepare_helpdesk_tickets_domain()
            domain += self.custom_helpdesk_domain()

            values['ticket_count'] = (
                request.env['helpdesk.ticket'].sudo().search_count(domain)
                if request.env['helpdesk.ticket'].check_access_rights('read', raise_exception=False)
                else 0
            )
        return values

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None,
                            groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        domain = self._prepare_helpdesk_tickets_domain()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'reference': {'label': _('Reference'), 'order': 'id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_id', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_id', '=', False)]},
            'open': {'label': _('Open'), 'domain': [('close_date', '=', False)]},
            'closed': {'label': _('Closed'), 'domain': [('close_date', '!=', False)]},
            'last_message_sup': {'label': _('Last message is from support')},
            'last_message_cust': {'label': _('Last message is from customer')},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'id': {'input': 'id', 'label': _('Search in Reference')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if filterby in ['last_message_sup', 'last_message_cust']:
            discussion_subtype_id = request.env.ref('mail.mt_comment').id
            messages = request.env['mail.message'].search_read(
                [('model', '=', 'helpdesk.ticket'), ('subtype_id', '=', discussion_subtype_id)],
                fields=['res_id', 'author_id'], order='date desc')
            last_author_dict = {}
            for message in messages:
                if message['res_id'] not in last_author_dict:
                    last_author_dict[message['res_id']] = message['author_id'][0]

            ticket_author_list = request.env['helpdesk.ticket'].search_read(fields=['id', 'partner_id'])
            ticket_author_dict = dict(
                [(ticket_author['id'], ticket_author['partner_id'][0] if ticket_author['partner_id'] else False) for
                 ticket_author in ticket_author_list])

            last_message_cust = []
            last_message_sup = []
            for ticket_id in last_author_dict.keys():
                if last_author_dict[ticket_id] == ticket_author_dict[ticket_id]:
                    last_message_cust.append(ticket_id)
                else:
                    last_message_sup.append(ticket_id)

            if filterby == 'last_message_cust':
                domain = AND([domain, [('id', 'in', last_message_cust)]])
            else:
                domain = AND([domain, [('id', 'in', last_message_sup)]])

        else:
            domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain = AND([domain, [('create_date', '>', date_begin), ('create_date', '<=', date_end)]])

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search),
                                                    ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in in ('status', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain = AND([domain, search_domain])

        # pager
        partner = request.env.user.partner_id
        domain += self.custom_helpdesk_domain()

        tickets_count = request.env['helpdesk.ticket'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in,
                      'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].sudo().search(domain, order=order, limit=self._items_per_page,offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in
                               groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        if partner and not partner.enable_helpdesk_portal_access:
            values = {}
        return request.render("helpdesk.portal_helpdesk_ticket", values)



