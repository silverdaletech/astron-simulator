# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.project.models.project import PROJECT_TASK_READABLE_FIELDS
PROJECT_TASK_READABLE_FIELDS.add("is_all_enable_timesheet")
PROJECT_TASK_READABLE_FIELDS.add("is_self_enable_timesheet")


class ResUser(models.Model):
    """inherit to add portal access right fields"""

    _inherit = 'res.partner'

    enable_timesheet_portal_access = fields.Boolean(string="Can see Timesheet on Portal", default=True)
    access_all_timesheet_records = fields.Boolean(string="Can see all company's Timesheet records", default=True)
    access_follower_timesheet_records = fields.Boolean(string="Can see  Timesheet records where he is a Follower", default=True)


    @api.onchange('enable_timesheet_portal_access')
    def check_timesheet_record_access(self):
        """uncheck the access on all company record in uncheck the enable sale portal access"""
        if not self.enable_timesheet_portal_access and self.access_all_timesheet_records:
            self.access_all_timesheet_records = False
            self.access_follower_timesheet_records = False


class AccountAnalyticLine1(models.Model):
    _inherit = 'account.analytic.line'

    def _timesheet_get_portal_domain(self):
        values = super(AccountAnalyticLine1, self)._timesheet_get_portal_domain()
        if self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            # Then, he is internal user, and we take the domain for this current user
            return self.env['ir.rule']._compute_domain(self._name)
        domain = []
        partner = self.env.user.partner_id
        if partner.enable_timesheet_portal_access and not partner.access_all_timesheet_records:
            if partner.access_follower_timesheet_records:
                domain += [('task_id.project_id.privacy_visibility', '=', 'portal'), '|',
                           ('task_id.partner_id', '=', partner.id),
                           ('task_id.message_follower_ids.partner_id', '=', partner.id)]
            else:
                domain += [('task_id.project_id.privacy_visibility', '=', 'portal'),
                           ('task_id.partner_id', '=', partner.id)]
        elif partner.access_follower_timesheet_records and not partner.access_all_timesheet_records:
            domain += [('task_id.project_id.privacy_visibility', '=', 'portal'),

                       '|', ('task_id.partner_id', '=', partner.id),
                       ('task_id.message_follower_ids.partner_id', '=', partner.id)
                       ]
        elif partner.enable_timesheet_portal_access and partner.access_all_timesheet_records and partner.access_follower_timesheet_records:
            domain += ['|', '|', '|', ('task_id.partner_id', 'child_of', partner.parent_id.id),
                       ('task_id.partner_id', '=', partner.id),
                       ('task_id.partner_id', 'in', partner.child_ids.ids),
                       ('task_id.message_follower_ids.partner_id', '=', partner.id),
                       ('task_id.project_id.privacy_visibility', '=', 'portal'),

                       ]
        elif partner.enable_timesheet_portal_access and partner.access_all_timesheet_records and not partner.access_follower_timesheet_records:
            domain += ['|', '|', ('task_id.partner_id', 'child_of', partner.parent_id.id),
                       ('task_id.partner_id', '=', partner.id),
                       ('task_id.partner_id', 'in', partner.child_ids.ids),
                       ('task_id.project_id.privacy_visibility', '=', 'portal'),

                       ]

        elif not partner.enable_timesheet_portal_access and not partner.access_all_timesheet_records:
            domain += [('task_id.project_id.privacy_visibility', '=', 'portal'),
                       ('task_id.is_timesheet_portal', '=', True),
                       ('task_id.partner_id', '=', partner.id)
                       ]
        domain.append(('task_id.is_timesheet_portal', '=', True))
        domain.append(('task_id.is_show_task', '=', True))

        return domain

    def _convert_hours_to_days(self, time):
        values = super(AccountAnalyticLine1, self)._convert_hours_to_days()
        uom_hour = self.env.ref('uom.product_uom_hour')
        uom_day = self.env.ref('uom.product_uom_day')
        partner = self.env.user.partner_id
        if partner.enable_timesheet_portal_access and not partner.access_all_timesheet_records:
            return None
        return round(uom_hour._compute_quantity(time, uom_day, raise_if_failure=False), 2)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_all_enable_timesheet = fields.Boolean(compute='_check_timesheet_access')
    is_self_enable_timesheet = fields.Boolean(compute='_check_timesheet_access')

    def _check_timesheet_access(self):
        partner = self.env.user.partner_id
        for task in self:
            if partner and task.partner_id.id==partner.id and partner.enable_timesheet_portal_access and not partner.access_all_timesheet_records:
                task.is_self_enable_timesheet = True
            else:
                task.is_self_enable_timesheet = False
            if partner and partner.enable_timesheet_portal_access and  partner.access_all_timesheet_records:
                task.is_all_enable_timesheet = True
            else:
                task.is_all_enable_timesheet = False









