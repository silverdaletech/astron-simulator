# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import fields, http, SUPERUSER_ID, _
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.purchase.controllers.portal import CustomerPortal
from collections import OrderedDict


class CustomerPortalInheritPurch(CustomerPortal):
    """Inherit to overwrite the access right of sale/quotation on portal"""

    def custom_domain(self):
        partner = request.env.user.partner_id
        domain = []
        if partner.enable_purchase_portal_access and not partner.access_all_purchase_records:
            domain.append(('partner_id', '=', partner.id))
        if partner.enable_follower_purchase_portal_access and not partner.access_all_purchase_records:
            domain.insert(0, '|')
            domain.append(('message_follower_ids.partner_id', '=', partner.id))
        if partner.access_all_purchase_records and partner.enable_follower_purchase_portal_access:

            domain.append(('message_follower_ids.partner_id', '=', partner.id))
            if partner.child_ids:
                domain.insert(0, '|')
                domain.append(('partner_id', 'in', partner.child_ids.ids))
            if partner.parent_id:
                domain.insert(0, '|')
                domain.insert(0, '|')
                domain.append(('partner_id', 'child_of', partner.parent_id.id))
                domain.append(('partner_id', '=', partner.parent_id.id))
        if partner.access_all_purchase_records and not partner.enable_follower_purchase_portal_access:

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

    def _prepare_portal_layout_values(self):
        """To enable or disable the access on portal"""
        values = super(CustomerPortalInheritPurch, self)._prepare_portal_layout_values()
        values['purchase_enable'] = False
        user_id = request.env['res.users'].browse(request.uid)
        partner_id = request.env['res.partner'].search([('user_ids', '=', user_id.id)], limit=1)
        if partner_id and partner_id.enable_purchase_portal_access:
            values['purchase_enable'] = True

        return values

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortalInheritPurch, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if partner and partner.enable_purchase_portal_access and not partner.access_all_purchase_records:
            pass
        PurchaseOrder = request.env['purchase.order']
        if 'rfq_count' in counters:
            domain = self.custom_domain()
            domain.append(('state','=','sent'))
            if domain:
                values['rfq_count'] = PurchaseOrder.sudo().search_count(domain) if PurchaseOrder.check_access_rights('read', raise_exception=False) else 0
            # elif partner.access_all_purchase_records and partner.enable_follower_purchase_portal_access:
            #     if partner.access_all_purchase_records and partner.enable_follower_purchase_portal_access:
            #         domain.insert(0, '&')
            #         domain.append(('message_follower_ids.partner_id', '=', partner.id))
            #         if partner.child_ids:
            #             domain.insert(0, '|')
            #             domain.append(('partner_id', 'in', partner.child_ids.ids))
            #         if partner.parent_id:
            #             domain.insert(0, '|')
            #             domain.append(('partner_id', 'child_of', partner.parent_id.id))
            #     values['rfq_count'] += PurchaseOrder.sudo().search_count([('message_follower_ids.partner_id','=',partner.id)])
        if 'purchase_count' in counters:

            domain = self.custom_domain()
            domain.append(('state', 'in', ['purchase', 'done', 'cancel']))

            if domain:
                values['purchase_count'] = PurchaseOrder.sudo().search_count(domain) if PurchaseOrder.check_access_rights('read', raise_exception=False) else 0
            # elif partner.access_all_purchase_records and partner.enable_follower_purchase_portal_access:
            #     if partner.access_all_purchase_records and partner.enable_follower_purchase_portal_access:
            #         domain.insert(0, '&')
            #         domain.append(('message_follower_ids.partner_id', '=', partner.id))
            #         if partner.child_ids:
            #             domain.insert(0, '|')
            #             domain.append(('partner_id', 'in', partner.child_ids.ids))
            #         if partner.parent_id:
            #             domain.insert(0, '|')
            #             domain.append(('partner_id', 'child_of', partner.parent_id.id))
            #     values['purchase_count'] += PurchaseOrder.sudo().search_count(domain)
        return values

    def _render_portal(self, template, page, date_begin, date_end, sortby, filterby, domain, searchbar_filters, default_filter, url, history, page_name, key):
        values = self._prepare_portal_layout_values()
        PurchaseOrder = request.env['purchase.order']
        partner = request.env.user.partner_id

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # if partner.enable_purchase_portal_access and not partner.access_all_purchase_records:


        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sort
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if searchbar_filters:
            # default filter
            if not filterby:
                filterby = default_filter
            domain += searchbar_filters[filterby]['domain']

        # count for pager
        domain += self.custom_domain()
        count = PurchaseOrder.sudo().search_count(domain)
        # if partner.access_all_purchase_records and partner.enable_follower_purchase_portal_access:
        #
        #
        #     count = PurchaseOrder.sudo().search_count(domain)




        # make pager
        pager = portal_pager(
            url=url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=count,
            page=page,
            step=self._items_per_page
        )

        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.sudo().search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session[history] = orders.ids[:100]

        values.update({
            'date': date_begin,
            key: orders,
            'page_name': page_name,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': url,
        })
        if not partner.enable_purchase_portal_access:
            values = {}
        return request.render(template, values)

