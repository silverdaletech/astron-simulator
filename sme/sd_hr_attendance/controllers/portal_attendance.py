# # -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        usr = http.request.env.user
        employee_id = usr.sudo().employee_id.id
        values = super()._prepare_home_portal_values(counters)
        if 'attendance_count' in counters:
            values['attendance_count'] = request.env['hr.attendance'].sudo().search_count([('employee_id', '=', employee_id)])
        return values

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendance(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        usr = http.request.env.user
        employee_id = usr.sudo().employee_id.id

        searchbar_sortings = {
            'employee_id': {'label': _('Employees'), 'order': 'employee_id asc'},
            'checked_in': {'label': _('Checked In'), 'order': 'check_in desc'},
            'checked_out': {'label': _('Checked Out'), 'order': 'check_out desc'},
            'worked_hours': {'label': _('Worked Hours'), 'order': 'worked_hours desc'},
        }

        searchbar_inputs = {
            'employee': {'input': 'employee_id', 'label': _('Search in Employees')},
            'checkoued_in': {'input': 'check_in', 'label': _('Search in (Checked In)')},
            'checkoued_out': {'input': 'check_out', 'label': _('Search in (Checked Out)')},
            'worked_hours': {'input': 'worked_hours', 'label': _('Search in Worked Hours')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        if not search_in:
            search_in = 'all'

        # default sort by value
        if not sortby:
            sortby = 'checked_in'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        def conv_float_time(value):
            try:
                vals = value.split(':')
                t, hours = divmod(float(vals[0]), 24)
                t, minutes = divmod(float(vals[1]), 60)
                minutes = minutes / 60.0
                return hours + minutes
            except:
                return "qz"
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('employee_id', 'all'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            if search_in in ('check_in', 'all'):
                search_domain = OR([search_domain, [('check_in', 'ilike', search)]])
            if search_in in ('check_out', 'all'):
                search_domain = OR([search_domain, [('check_out', 'ilike', search)]])
            if search_in in ('worked_hours', 'all'):
                float_time = conv_float_time(search)
                if not float_time == 'qz':
                    hr_vals = request.env['hr.attendance'].sudo().search([])
                    for hr in hr_vals:
                        if hr.worked_hours == float_time:
                            search_domain = OR([search_domain, [('id', '=', hr.id)]])
            domain += search_domain
        domain += [('employee_id', '=', employee_id)]
        attendance_count = request.env['hr.attendance'].sudo().search_count(domain)
        _items_per_page = 100
        # pager
        pager = portal_pager(
            url="/my/attendance",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=attendance_count,
            page=page,
            step=_items_per_page
        )

        _attendance = request.env['hr.attendance'].sudo().search(domain, order=order, limit=_items_per_page, offset=pager['offset'])
        request.session['my_attendance_history'] = _attendance.ids[:100]
        grouped_attendance = [_attendance]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_attendance': grouped_attendance,
            'page_name': 'attendance',
            'default_url': '/my/attendance',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
        })
        return request.render("sd_hr_attendance.portal_my_attendance", values)
