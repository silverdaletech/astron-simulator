# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

from odoo.exceptions import ValidationError, UserError, AccessError


class TestScript(models.Model):
    _name = 'project.test.script'
    _description = 'TestScript'
    _order = 'sequence'

    name = fields.Char('Test Script Name')
    priority = fields.Selection(
        string='Priority', selection=[('0', 'Normal'),
                                      ('1', 'Low'),
                                      ('2', 'High'),
                                      ('3', 'Very High'), ])

    partner_id = fields.Many2many('res.partner', string='Clients')
    test_script_expected_result = fields.Text(string="Expected Result")
    test_script_detail = fields.Text(string="Steps to Reproduce")
    test_script_ticket_ids = fields.One2many(
        comodel_name='helpdesk.ticket',
        inverse_name='project_test_script_id',
        string='Tickets')
    test_script_task_ids = fields.Many2many('project.task', string='Tasks')
    test_script_project_ids = fields.Many2many('project.project', string='Projects')
    sequence = fields.Integer(string='Sequence')

    studio_fields_data = fields.Text(string=" Studio Fields Data")
    group_id = fields.Many2one('res.groups', string='Access Level')
    active = fields.Boolean(string='Active', default=True)

    # Todo: Will remove this field once we start filling WS field
    section = fields.Char('Section')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_testscript_ids = fields.Many2many('project.test.script', string='Test Scripts')


class Project(models.Model):
    _inherit = 'project.project'

    project_testscript_ids = fields.Many2many('project.test.script', string='Test Scripts', compute='_compute_test_scripts')

    def _compute_test_scripts(self):
        self.project_testscript_ids = False
        if self.task_ids:
            test_scripts = []
            for task in self.task_ids:
                if task.task_testscript_ids:
                    for script in task.task_testscript_ids:
                        test_scripts.append(script.id)
            #  In the below lines it will updated and create all the test scripts from the task related to this project.
            project_script = [(6, 0, test_scripts)]

            self.project_testscript_ids = project_script


class TICKETS(models.Model):
    _inherit = 'helpdesk.ticket'

    project_test_script_id = fields.Many2one('project.test.script', string='Test Script')
    test_script_priority = fields.Selection(
        string='Test Script Priority', selection=[('0', 'Normal'),
                                                  ('1', 'Low'),
                                                  ('2', 'High'),
                                                  ('3', 'Very High'), ], related='project_test_script_id.priority')
