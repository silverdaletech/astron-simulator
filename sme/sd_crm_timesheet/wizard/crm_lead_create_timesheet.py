# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CRMLeadCreateTimesheet(models.TransientModel):
    _name = 'crm.lead.create.timesheet'
    _description = "Create Timesheet from Lead"

    _sql_constraints = [('time_positive', 'CHECK(time_spent > 0)', 'The timesheet\'s time must be positive' )]

    time_spent = fields.Float('Time', digits=(16, 2))
    description = fields.Char('Description')
    lead_id = fields.Many2one(
        'crm.lead', "Task", required=True,
        default=lambda self: self.env.context.get('active_id', None),
        help="Lead for which we are creating a sales order",
    )

    def save_timesheet(self):
        # Not calling super as def deprecated in hr_timesheet.
        # The wizard has to be moved to timesheet_grid in master.
        employee_id = False
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)])
        if employee:
            employee_id = employee.id
        values = {
            'lead_id': self.lead_id.id,
            'date': fields.Date.context_today(self),
            'name': self.description or '/',
            'user_id': self.env.uid,
            'employee_id': employee_id,
            'unit_amount': self.lead_id._get_rounded_hours(self.time_spent * 60),
        }
        self.lead_id.user_timer_id.unlink()
        return self.env['account.analytic.line'].create(values)

    def action_delete_timesheet(self):
        self.lead_id.user_timer_id.unlink()
