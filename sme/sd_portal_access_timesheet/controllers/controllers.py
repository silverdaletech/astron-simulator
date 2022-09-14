# -*- coding: utf-8 -*-

from odoo.http import request
from operator import itemgetter
from markupsafe import Markup
from odoo import fields, http, SUPERUSER_ID, _
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import  pager as portal_pager
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
from datetime import datetime
from odoo.osv.expression import OR, AND
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils, groupby as groupbyelem


class CustomerPortalInheritTimesheet(TimesheetCustomerPortal):
    """Inherit to overwrite the access right of sale/quotation on portal"""

    def _prepare_portal_layout_values(self):
        """To enable or disable the access on portal"""
        values = super(CustomerPortalInheritTimesheet, self)._prepare_portal_layout_values()
        values['timesheet_enable'] = False
        values['enable_hours'] = False
        user_id = request.env['res.users'].browse(request.uid)
        partner_id = request.env['res.partner'].search([('user_ids', '=', user_id.id)], limit=1)
        if partner_id and partner_id.enable_timesheet_portal_access:
            values['timesheet_enable'] = True
        if partner_id and partner_id.enable_timesheet_portal_access and not partner_id.access_all_timesheet_records:
            values['enable_hours'] = True

        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'timesheet_count' in counters:
            Timesheet = request.env['account.analytic.line']
            domain = Timesheet._timesheet_get_portal_domain()
            values['timesheet_count'] = Timesheet.sudo().search_count(domain)
        return values



    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
        Timesheet = request.env['account.analytic.line']
        domain = Timesheet._timesheet_get_portal_domain()
        Timesheet_sudo = Timesheet.sudo()

        values = self._prepare_portal_layout_values()
        _items_per_page = 100

        searchbar_sortings = self._get_searchbar_sortings()

        searchbar_inputs = self._get_searchbar_inputs()

        searchbar_groupby = self._get_searchbar_groupby()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")),
                                                         ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')),
                                                           ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')),
                                                         ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")),
                                                              ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date', '>=', date_utils.start_of(last_month, 'month')),
                                                                ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')),
                                                              ('date', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain += self._get_search_domain(search_in, search)
        partner = request.env.user.partner_id
        # if partner.enable_timesheet_portal_access and not partner.access_all_timesheet_records:
        #
        #     domain.append(('task_id.partner_id','=',partner.id))
        timesheet_count = Timesheet_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/timesheets",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby, 'groupby': groupby},
            total=timesheet_count,
            page=page,
            step=_items_per_page
        )

        def get_timesheets():
            groupby_mapping = self._get_groupby_mapping()
            field = groupby_mapping.get(groupby, None)
            orderby = '%s, %s' % (field, order) if field else order
            timesheets = Timesheet_sudo.search(domain, order=orderby, limit=_items_per_page, offset=pager['offset'])
            if field:
                if groupby == 'date':
                    time_data = Timesheet_sudo.read_group(domain, ['date', 'unit_amount:sum'], ['date:day'])
                    mapped_time = dict(
                        [(datetime.strptime(m['date:day'], '%d %b %Y').date(), m['unit_amount']) for m in time_data])
                    grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k]) for k, g in
                                          groupbyelem(timesheets, itemgetter('date'))]
                else:
                    time_data = time_data = Timesheet_sudo.read_group(domain, [field, 'unit_amount:sum'], [field])
                    mapped_time = dict([(m[field][0] if m[field] else False, m['unit_amount']) for m in time_data])
                    grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g in
                                          groupbyelem(timesheets, itemgetter(field))]
                return timesheets, grouped_timesheets

            grouped_timesheets = [(
                timesheets,
                sum(Timesheet_sudo.search(domain).mapped('unit_amount'))
            )] if timesheets else []
            return timesheets, grouped_timesheets

        timesheets, grouped_timesheets = get_timesheets()

        values.update({
            'timesheets': timesheets,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'timesheet',
            'default_url': '/my/timesheets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'is_uom_day': request.env['account.analytic.line']._is_timesheet_encode_uom_day(),
        })
        if not partner.enable_timesheet_portal_access:
            values = {}

        return request.render("hr_timesheet.portal_my_timesheets", values)
