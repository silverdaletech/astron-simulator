from odoo import models, fields, api, _


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    close_stage_id = fields.Many2one(
        comodel_name='helpdesk.stage',
        string='Close Stage',
        required=False)
    project_stage_ids = fields.Many2many('project.project.stage', string='Project Stages',
                                         help="stages for project visible on ticket")
