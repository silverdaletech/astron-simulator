# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    solution = fields.Html(string="Solution", required=False)
    task_project_id = fields.Many2one("project.project", 'Task Project', tracking=True)
    project_status = fields.Char(string='Project Status', related='project_id.stage_id.name', store=True,
                                 tracking=True)
    project_status_initial = fields.Char(string='Project Status When Attached',
                                         compute='compute_project_status_initial', store=True, tracking=True)
    task_id = fields.Many2one("project.task", 'Task')
    task_ids = fields.Many2many("project.task", string='Tasks')
    task_count = fields.Integer(compute="_compute_tasks_count")
    task_stage_ids = fields.Many2many('project.task.type', string='Tasks Stages', compute="_compute_tasks_count",
                                      store=True)
    project_stage_ids = fields.Many2many('project.project.stage', 'ticket_project_stage_rel', 'ticket_id',
                                         'project_stage_id', string='Project stages',
                                         related='team_id.project_stage_ids',)
    rootcause_id = fields.Many2one('ticket.rootcause', string='Rootcause')

    @api.depends('task_ids')
    def _compute_tasks_count(self):
        for ticket in self:
            ticket.task_count = len(ticket.task_ids)
            ticket.task_stage_ids = ticket.task_ids.mapped('stage_id').ids

    @api.onchange('task_ids')
    def update_task_stage_ids(self):
        for ticket in self:
            ticket._compute_tasks_count()
            if not ticket.task_ids:
                ticket.task_stage_ids = False

    def open_tasks_view(self):
        if len(self.task_ids) > 1:
            views = 'tree,form'
            res_id = False
            domain = "[('id', 'in', %s)]" % self.task_ids.ids
        else:
            views = 'form'
            res_id = self.task_ids.id
            domain = False
        return {
            'name': _('Tasks'),
            'view_mode': views,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'res_id': res_id,
            "context": {'default_ticket_ids': [(4, self.id)]},
        }

    @api.depends('project_id')
    def compute_project_status_initial(self):
        for rec in self:
            rec.project_status_initial = ''
            if rec.project_id and rec.project_id.stage_id:
                rec.project_status_initial = rec.project_id.stage_id.name
