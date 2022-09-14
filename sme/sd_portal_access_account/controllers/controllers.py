# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import fields, http, SUPERUSER_ID, _
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.osv.expression import OR

class CustomerPortalInheritInvoice(PortalAccount):
    """Inherit to overwrite the access right of sale/quotation on portal"""

    def _prepare_portal_layout_values(self):
        """To enable or disable the access on portal"""
        values = super(CustomerPortalInheritInvoice, self)._prepare_portal_layout_values()
        values['invoice_enable'] = False
        user_id = request.env['res.users'].browse(request.uid)
        partner_id = request.env['res.partner'].search([('user_ids', '=', user_id.id)], limit=1)
        if partner_id and partner_id.enable_invoice_portal_access:
            values['invoice_enable'] = True

        return values

    def custom_invoice_domain(self):
        partner = request.env.user.partner_id
        domain = []
        if partner.enable_invoice_portal_access and not partner.access_all_invoice_records:
            domain.append(('partner_id', '=', partner.id))
        if partner.enable_follower_invoice_portal_access and not partner.access_all_invoice_records:
            domain.insert(0, '|')
            domain.append(('message_follower_ids.partner_id', '=', partner.id))
        if partner.access_all_invoice_records and partner.enable_follower_invoice_portal_access:

            domain.append(('message_follower_ids.partner_id', '=', partner.id))
            if partner.child_ids:
                domain.insert(0, '|')
                domain.append(('partner_id', 'in', partner.child_ids.ids))
            if partner.parent_id:
                domain.insert(0, '|')
                domain.insert(0, '|')
                domain.append(('partner_id', 'child_of', partner.parent_id.id))
                domain.append(('partner_id', '=', partner.parent_id.id))

        if partner.access_all_invoice_records and not partner.enable_follower_invoice_portal_access:

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

        values = super(CustomerPortalInheritInvoice, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        invoice = request.env['account.move']
        if 'invoice_count' in counters:
            domain = self._get_invoices_domain()
            domain += self.custom_invoice_domain()
            invoice_count = request.env['account.move'].sudo().search_count(domain) \
                if request.env['account.move'].check_access_rights('read', raise_exception=False) else 0
            values['invoice_count'] = invoice_count


        return values




    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, search=None, search_in=None, sortby=None, groupby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']
        partner = request.env.user.partner_id

        domain = self._get_invoices_domain()
        domain += self.custom_invoice_domain()
        # if partner.enable_invoice_portal_access and not partner.access_all_invoice_records:
        #     domain.append(('partner_id', '=', partner.id))

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # this is the code to add search bar for name and customer reference search
        #-------------------------------------------------------------------------------------------------------------
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Name'), 'order': 1},
            'ref': {'input': 'ref', 'label': _('Search in Customer Reference'), 'order': 2},
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 3},
        }
        if not search_in:
            search_in = 'all'
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('ref', 'all'):
                search_domain = OR([search_domain, [('ref', 'ilike', search)]])
            domain += search_domain

        #-------------------------------------------------------------------------------------------------------------

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'groupby': groupby, 'search_in': search_in, 'search': search},
            url="/my/invoices",
            # url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]
        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,

        })
        if not partner.enable_invoice_portal_access:
            values = {}
        return request.render("account.portal_my_invoices", values)
