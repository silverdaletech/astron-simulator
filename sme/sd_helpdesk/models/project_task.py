# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    ticket_ids = fields.Many2many("helpdesk.ticket", string='Tickets')
    ticket_count = fields.Integer(compute="_compute_tickets_count")

    @api.depends('ticket_ids')
    def _compute_tickets_count(self):
        for task in self:
            task.ticket_count = len(task.ticket_ids)

    def open_tickets_view(self):
        if len(self.ticket_ids) > 1:
            views = 'tree,form'
            res_id = False
            domain = "[('id', 'in', %s)]" % self.ticket_ids.ids
        else:
            views = 'form'
            res_id = self.ticket_ids.id
            domain = False
        return {
            'name': _('Ticket'),
            'view_mode': views,
            'res_model': 'helpdesk.ticket',
            'domain': domain,
            'view_id': False,
            'res_id': res_id,
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
