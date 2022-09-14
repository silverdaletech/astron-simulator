# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models, fields, api
from odoo.addons.project.models.project import PROJECT_TASK_READABLE_FIELDS
PROJECT_TASK_READABLE_FIELDS.add("task_count_with_subtasks_custom")



class ResUser(models.Model):
    """inherit to add portal access right fields"""

    _inherit = 'res.partner'

    enable_project_portal_access = fields.Boolean(string="Can see Project and Task on Portal", default=True)
    access_all_project_records = fields.Boolean(string="Can see all company's Project and task records", default=True  )
    access_follower_project_records = fields.Boolean(string="Can see Project and task records Where he is follower", default=True  )

    @api.onchange('enable_project_portal_access')
    def check_project_record_access(self):
        """uncheck the access on all company record in uncheck the enable sale portal access"""
        if not self.enable_project_portal_access and self.access_all_project_records:
            self.access_all_project_records = False
            self.access_follower_project_records = False


class ProjectInherit(models.Model):
    _inherit = 'project.project'
    task_count_with_subtasks_custom = fields.Integer(compute='_compute_task_count_custom')
    # moved from sd_project_portal
    task_count_with_subtasks_portal2 = fields.Integer(compute='_compute_task_count_portal')

    def _compute_task_count_custom(self):

        partner = self.env.user.partner_id
        for project in self:
            if partner and  partner.enable_project_portal_access and not partner.access_all_project_records:
                if partner.access_follower_project_records:
                    project.task_count_with_subtasks_custom = self.env['project.task'].sudo().search_count([('project_id', '=', project.id),'|',('partner_id', '=', partner.ids),('message_follower_ids.partner_id', '=', partner.id)])
                else:
                    project.task_count_with_subtasks_custom = self.env['project.task'].sudo().search_count([('project_id', '=', project.id),('partner_id', '=', partner.ids)])
            else:
                project.task_count_with_subtasks_custom = self.env['project.task'].sudo().search_count(
                    ['|', '|','|',('partner_id', '=', partner.ids),('message_follower_ids.partner_id', '=', partner.id), ('partner_id', 'in', partner.child_ids.ids),('partner_id', 'child_of', partner.parent_id.id),('project_id', '=', project.id)])

        return super(ProjectInherit, self)._compute_task_count_custom()

#     moved from sd_project_portal
    def _compute_task_count_portal(self):
        """
            this is the method used to update field "task_count_with_subtasks_portal2" value to
            count the tasks according to boolean field on task form
            if that field is checked there on task form , it is for portal to count tasks
        """
        task_data = self.env['project.task'].read_group(
            [('is_show_task', '=', True), ('project_id', 'in', self.ids),
             '|',
                ('stage_id.fold', '=', False),
                ('stage_id', '=', False)],
            ['project_id', 'display_project_id:count'], ['project_id'])
        result_wo_subtask = defaultdict(int)
        result_with_subtasks = defaultdict(int)
        for data in task_data:
            result_wo_subtask[data['project_id'][0]] += data['display_project_id']
            result_with_subtasks[data['project_id'][0]] += data['project_id_count']
        for project in self:
            project.task_count_with_subtasks_portal2 = result_with_subtasks[project.id]

    #     moved from sd_project_portal
    @api.onchange('privacy_visibility')
    def _on_change_privacy_visibility(self):
        """
            this onchange method will make task to display on portal if
            "privacy_visibility" is not set to "portal"
        """
        for rec in self:
            str_id = str(rec.id)
            try:
                id = int(str_id)
            except:
                id = int(''.join(x for x in str_id if x.isdigit()))
            if rec.privacy_visibility != 'portal':
                tasks = self.env['project.task'].search([('project_id', '=', id)])
                for task in tasks:
                    task.write({'is_show_task': True})







