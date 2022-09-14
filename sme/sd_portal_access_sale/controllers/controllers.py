# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import fields, http, SUPERUSER_ID, _
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortalInherit(CustomerPortal):
    """Inherit to overwrite the access right of sale/quotation on portal"""

    def _prepare_portal_layout_values(self):
        """To enable or disable the access on portal"""
        values = super(CustomerPortalInherit, self)._prepare_portal_layout_values()
        values['sale_enable'] = False
        user_id = request.env['res.users'].browse(request.uid)
        partner_id = request.env['res.partner'].search([('user_ids', '=', user_id.id)], limit=1)
        if partner_id and partner_id.enable_sale_portal_access:
            values['sale_enable'] = True

        return values

    def custom_sale_domain(self):
        partner = request.env.user.partner_id
        domain = []

        if partner.enable_sale_portal_access and not partner.access_all_records:
            domain.append(('partner_id', '=', partner.id))

        if partner.access_follower_sale_records and not partner.access_all_records:
            domain.insert(0, '|')
            domain.append(('message_follower_ids.partner_id', '=', partner.id))

        if partner.access_all_records and partner.access_follower_sale_records:
            domain.insert(0, '|')
            domain.append(('partner_id', '=', partner.id))
            domain.append(('message_follower_ids.partner_id', '=', partner.id))
            if partner.child_ids:
                domain.insert(0, '|')
                domain.append(('partner_id', 'in', partner.child_ids.ids))
            if partner.parent_id:
                domain.insert(0, '|')
                domain.insert(0, '|')
                domain.append(('partner_id', 'child_of', partner.parent_id.id))
                domain.append(('partner_id', '=', partner.parent_id.id))
        if partner.access_all_records and not partner.access_follower_sale_records:

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

        values = super(CustomerPortalInherit, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if partner and partner.enable_sale_portal_access and not partner.access_all_records:
            pass
        SaleOrder = request.env['sale.order']
        if 'quotation_count' in counters:
            domain = self.custom_sale_domain()
            domain.append(('state', 'in', ['sent', 'cancel']))

            values['quotation_count'] = SaleOrder.sudo().search_count(domain) \
                if SaleOrder.check_access_rights('read', raise_exception=False) else 0
        if 'order_count' in counters:

            domain = self.custom_sale_domain()
            domain.append(('state', 'in', ['sale', 'done']))
            values['order_count'] = SaleOrder.sudo().search_count(domain) \
                if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        return values

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = super(CustomerPortalInherit, self).portal_my_quotes()
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = self._prepare_quotations_domain(partner)
        domain = self.custom_sale_domain()
        domain.append(('state', 'in', ['sent', 'cancel']))
        # if partner.enable_sale_portal_access and not partner.access_all_records:
        #     if ('message_partner_ids', 'child_of', [partner.id]) in domain:
        #         domain.remove(('message_partner_ids', 'child_of', [partner.id]))
        #     domain.append(('partner_id', '=', partner.id))

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page,
                                      offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        if not partner.enable_sale_portal_access:
            values = {}

        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = self._prepare_orders_domain(partner)
        domain = self.custom_sale_domain()
        domain.append(('state', 'in', ['sale', 'done']))

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        orders = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        if not partner.enable_sale_portal_access:
            values = {}
        return request.render("sale.portal_my_orders", values)
