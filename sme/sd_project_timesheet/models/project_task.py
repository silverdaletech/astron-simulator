# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTaskInherit(models.Model):
    _inherit = "project.task"

    non_billable = fields.Boolean(string='Non-Billable')

    @api.onchange('non_billable')
    def onchange_non_billable(self):
        if self.non_billable:
            for rec in self.timesheet_ids.filtered(lambda p: p.validated_status != 'validated' or p.non_billable and p.validated_status == 'validated'):
                if not rec.timesheet_invoice_id:
                    rec.so_line = False
            if not any(timesheet.so_line for timesheet in self.timesheet_ids):
                self.sale_line_id = False
        else:
            self.sale_line_id = self.display_project_id.sale_line_id.id
            if self.timesheet_ids:
                for rec in self.timesheet_ids:
                    if rec.non_billable:
                        rec.so_line = False
                    else:
                        # rec.non_billable = False
                        rec.so_line = self.display_project_id.sale_line_id.id

    @api.onchange('task_type_id')
    def onchange_task_type_id(self):
        """
            this method will set non_billable field True or False according to the task_type selection field.
            if task_type selection field has its boolean field 'hide_from_portal' True, then non_billable
            field will be True, and vise versa.
        """

        for rec in self:
            if rec.task_type_id:
                if rec.task_type_id.hide_from_portal:
                    rec.non_billable = True
                else:
                    rec.non_billable = False
