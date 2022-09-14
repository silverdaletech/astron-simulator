# -*- coding: utf-8 -*-

from odoo.http import request
from operator import itemgetter
from markupsafe import Markup
from odoo import fields, http, SUPERUSER_ID, _
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.project.controllers.portal import ProjectCustomerPortal
# from odoo.addons.sd_project_portal.controllers.controllers import ProjectCustomerPortal2
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR, AND


class CustomerPortalInheritProject(ProjectCustomerPortal):
    """Inherit to overwrite the access right of sale/quotation on portal"""

    def _prepare_portal_layout_values(self):
        """To enable or disable the access on portal"""
        values = super(CustomerPortalInheritProject, self)._prepare_portal_layout_values()
        values['project_enable'] = False
        user_id = request.env['res.users'].browse(request.uid)
        partner_id = request.env['res.partner'].search([('user_ids', '=', user_id.id)], limit=1)
        if partner_id and partner_id.enable_project_portal_access:
            values['project_enable'] = True

        return values

    def custom_project_domain(self):
        partner = request.env.user.partner_id
        domain = []
        if partner.enable_project_portal_access and not partner.access_all_project_records:
            domain.append(('partner_id', '=', partner.id))

        if partner.access_follower_project_records and not partner.access_all_project_records:
            domain.insert(0, '|')
            domain.append(('message_follower_ids.partner_id', '=', partner.id))

        if partner.access_all_project_records and partner.access_follower_project_records:

            domain.append(('message_follower_ids.partner_id', '=', partner.id))
            if partner.child_ids:
                domain.insert(0, '|')
                domain.append(('partner_id', 'in', partner.child_ids.ids))
            if partner.parent_id:
                domain.insert(0, '|')
                domain.insert(0, '|')
                domain.append(('partner_id', 'child_of', partner.parent_id.id))
                domain.append(('partner_id', '=', partner.parent_id.id))
        if partner.access_all_project_records and not partner.access_follower_project_records:

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

        if partner:
            if 'project_count' in counters:
                domain = self.custom_project_domain()
                values['project_count'] = request.env['project.project'].sudo().search_count(domain)
            if 'task_count' in counters :
                domain = self.custom_project_domain()
                domain.append(('is_show_task', '=', True))
                values['task_count'] = request.env['project.task'].sudo().search_count(domain)

        return values

    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                        search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._task_get_searchbar_sortings()
        searchbar_sortings = dict(sorted(self._task_get_searchbar_sortings().items(),
                                         key=lambda item: item[1]["sequence"]))
        partner = request.env.user.partner_id

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = self._task_get_searchbar_inputs()
        searchbar_groupby = self._task_get_searchbar_groupby()

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].sudo().search([])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
            })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
                                                                ['project_id'], ['project_id'])
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name = group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # default group by value
        if not groupby:
            groupby = 'project'

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            domain += self._task_get_search_domain(search_in, search)

        TaskSudo = request.env['project.task'].sudo()
        domain = AND([domain, request.env['ir.rule']._compute_domain(TaskSudo._name, 'read')])

        # task count

        domain += self.custom_project_domain()
        domain.append(('is_show_task', '=', True))

        task_count = TaskSudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'groupby': groupby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        order = self._task_get_order(order, groupby)

        tasks = TaskSudo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tasks_history'] = tasks.ids[:100]

        groupby_mapping = self._task_get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_tasks = [request.env['project.task'].concat(*g) for k, g in groupbyelem(tasks, itemgetter(group))]
        else:
            grouped_tasks = [tasks]

        task_states = dict(request.env['project.task']._fields['kanban_state']._description_selection(request.env))
        if sortby == 'status':
            if groupby == 'none' and grouped_tasks:
                grouped_tasks[0] = grouped_tasks[0].sorted(lambda tasks: task_states.get(tasks.kanban_state))
            else:
                grouped_tasks.sort(key=lambda tasks: task_states.get(tasks[0].kanban_state))

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'task',
            'default_url': '/my/tasks',
            'task_url': 'task',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        if partner and not partner.enable_project_portal_access:
            values = {}
        return request.render("project.portal_my_tasks", values)

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Project = request.env['project.project']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # projects count
        partner = request.env.user.partner_id
        domain += self.custom_project_domain()

        project_count = Project.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        projects = Project.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_projects_history'] = projects.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'page_name': 'project',
            'default_url': '/my/projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        if not partner.enable_project_portal_access:
            values = {}
        return request.render("project.portal_my_projects", values)

    def _project_get_page_view_values(self, project, access_token, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', groupby=None, **kwargs):
        usr = http.request.env.user
        user_id = usr.partner_id
        domain = []
        is_portal_user = http.request.env.user.has_group('base.group_portal')

        # TODO: refactor this because most of this code is duplicated from portal_my_tasks method
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._task_get_searchbar_sortings()

        searchbar_inputs = self._task_get_searchbar_inputs()
        searchbar_groupby = self._task_get_searchbar_groupby()
        # task count
        partner = request.env.user.partner_id
        domain += self.custom_project_domain()
        domain.append(('is_show_task', '=', True))

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        domain += [('project_id', '=', project.id)]

        # default group by value
        if not groupby:
            groupby = 'project'

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            domain += self._task_get_search_domain(search_in, search)

        Task = request.env['project.task']
        if access_token:
            Task = Task.sudo()


        task_count = Task.sudo().search_count(domain)
        # pager
        url = "/my/project/%s" % project.id
        pager = portal_pager(
            url=url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        order = self._task_get_order(order, groupby)

        tasks = Task.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        if not is_portal_user:
            tasks = request.env['project.task'].sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        else:
            project_ids = []
            task_ids = []
            for task in tasks:
                project_ids.append(task.project_id)
            project_ids = set(project_ids)
            for project in project_ids:
                # prj = request.env['project.project'].search([('partner_id', '=', user_id.id)])
                # if not prj.id:
                prjct = request.env['project.project'].sudo().search([('id', '=', project.id)])
                company_falg = 0
                customer = prjct.partner_id.id
                customer_company = request.env['res.partner'].sudo().search([('id','=',customer)]).parent_id.id
                user_company = request.env['res.partner'].sudo().search([('id','=',user_id.id)]).parent_id.id

                if customer_company == user_company:
                    company_falg = 1
                if not customer_company:
                    company_falg = 0
                if prjct.partner_id.id == user_id.id or company_falg:
                    all_task = request.env['project.task'].search(
                        [('project_id', '=', project.id)])
                else:
                    all_task = request.env['project.task'].search([('project_id', '=', project.id)])
                for task in all_task:
                    task_ids.append(task)

            task_ids_lst = []
            for task in task_ids:
                task_ids_lst.append(task.id)
            tasks_ids_lst = []
            for task in tasks:
                tasks_ids_lst.append(task.id)
            commen_ids = list(set(task_ids_lst)&set(tasks_ids_lst))

            tasks = tasks.search([('id', 'in', commen_ids)])

            task_count_lst = []
            for task in tasks:
                task_count_lst.append(task.id)
            task_count = len(task_count_lst)

            tasks = request.env['project.task'].search([('id', 'in', commen_ids)], order=order, limit=self._items_per_page, offset=pager['offset'])





        request.session['my_project_tasks_history'] = tasks.ids[:100]

        groupby_mapping = self._task_get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_tasks = [Task.concat(*g) for k, g in groupbyelem(tasks, itemgetter(group))]
        else:
            grouped_tasks = [tasks]

        values.update(
            date=date_begin,
            date_end=date_end,
            grouped_tasks=grouped_tasks,
            page_name='project',
            default_url=url,
            pager=pager,
            searchbar_sortings=searchbar_sortings,
            searchbar_groupby=searchbar_groupby,
            searchbar_inputs=searchbar_inputs,
            search_in=search_in,
            search=search,
            sortby=sortby,
            groupby=groupby,
            project=project,
        )
        return self._get_page_view_values(project, access_token, values, 'my_projects_history', False, **kwargs)




