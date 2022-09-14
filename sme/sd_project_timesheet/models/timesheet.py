# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    non_billable = fields.Boolean(string='Non-Billable')
    is_toggle = fields.Boolean(compute='_compute_is_toggle')

    task_type_id = fields.Many2one('task.type', string='Task Type', related='task_id.task_type_id', store=True)

    @api.depends('task_id.non_billable')
    def _compute_is_toggle(self):
        """
        this method will hide toggle button if non_billable toggle button on ticket form view is checked
        """
        for rec in self:
            rec.is_toggle = rec.task_id.non_billable


    @api.depends('task_id.non_billable')
    def _compute_is_toggle(self):
        """
        this method will hide toggle button if non_billable toggle button on task form view is checked
        """
        for rec in self:
            rec.is_toggle = rec.task_id.non_billable

    # def _timesheet_get_portal_domain(self):
    #     res = super(AccountAnalyticLine, self)._timesheet_get_portal_domain()
    #     # This domain will add a validation to show only timesheet whose tasks,  task type is not hide from portal.
    #     # res += [('task_id.task_type_id.hide_from_portal', '=', False)]
    #     res += ['|', ('task_id.task_type_id.hide_from_portal', '=', False), ('task_id.task_type_id', '=', False)]
    #     return res

