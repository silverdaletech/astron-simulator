# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HelpdeskTicketCreateTimesheetInherit(models.TransientModel):
    _inherit = 'helpdesk.ticket.create.timesheet'

    def action_generate_timesheet(self):
        res = super(HelpdeskTicketCreateTimesheetInherit, self).action_generate_timesheet()
        if self.ticket_id:
            if self.ticket_id.non_billable:
                res.write({'so_line': False})
        return res
