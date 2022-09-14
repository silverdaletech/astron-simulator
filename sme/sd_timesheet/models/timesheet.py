# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    non_billable = fields.Boolean(string='Non-Billable')
    is_toggle = fields.Boolean(compute='_compute_is_toggle')
    is_helpdesk_toggle = fields.Boolean(compute='_compute_is_helpdesk_toggle')
    parent_id = fields.Many2one(string='Manager', related='employee_id.parent_id', store=True)
    timesheet_manager_id = fields.Many2one(string='Timesheet Approver', related='employee_id.timesheet_manager_id',
                                           store=True)

    @api.depends('task_id.sale_line_id', 'project_id.sale_line_id', 'employee_id', 'project_id.allow_billable', 'helpdesk_ticket_id.sale_line_id')
    def _compute_so_line(self):
        # non_billed_helpdesk_timesheets = self.filtered(lambda t: not t.is_so_line_edited and t.helpdesk_ticket_id and t._is_not_billed())
        non_billed_timesheets = self.filtered(lambda t: not t.is_so_line_edited and t._is_not_billed())
        for timesheet in non_billed_timesheets:
            if timesheet.non_billable:
                timesheet.so_line = False
            else:
                if timesheet.helpdesk_ticket_id:
                    timesheet.so_line = timesheet.project_id.allow_billable and timesheet.helpdesk_ticket_id.sale_line_id
                else:
                    timesheet.so_line = timesheet.project_id.allow_billable and timesheet._timesheet_determine_sale_line()
        super(AccountAnalyticLine, self - non_billed_timesheets)._compute_so_line()

    @api.onchange('non_billable')
    def onchange_non_billable_timesheet_linea(self):
        """
        this will remove and add so in timesheet line individually
        """
        for record in self:
            if record.validated_status != 'validated':
                if record.non_billable:
                    record.so_line = None
                else:
                    if record.task_id:
                        record.so_line = record.task_id.sale_line_id.id
                    else:
                        record.so_line = record.helpdesk_ticket_id.sale_line_id.id if record.helpdesk_ticket_id else None
            else:
                if record.validated_status == 'validated' and record.non_billable:
                    record.so_line = False
