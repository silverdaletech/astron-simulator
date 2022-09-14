# -*- coding: utf-8 -*-
from odoo import api, fields, models
from collections import defaultdict


class ProjectInherit(models.Model):
    _inherit = 'project.project'

    # def _compute_task_count_custom(self):
    #     task_data = self.env['project.task'].read_group(
    #         [('project_id', 'in', self.ids), '|', ('task_type_id.hide_from_portal', '=', False), ('task_type_id', '=', False),
    #          '|',
    #             ('stage_id.fold', '=', False),
    #             ('stage_id', '=', False)],
    #         ['project_id', 'display_project_id:count'], ['project_id'])
    #     result_with_subtasks = defaultdict(int)
    #     for data in task_data:
    #         result_with_subtasks[data['project_id'][0]] += data['project_id_count']
    #     for project in self:
    #         project.task_count_with_subtasks_custom = result_with_subtasks[project.id]
    #     return super(ProjectInherit, self)._compute_task_count_custom()
