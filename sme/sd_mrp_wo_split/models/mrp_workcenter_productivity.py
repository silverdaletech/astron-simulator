from email.policy import default
from odoo import models, fields, api, _ 


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    produced_qty = fields.Float(default=0)
    produced_range = fields.Char(string="Range")
    badge_number = fields.Char(string="Badge/ID", readonly=True)
    employee_id = fields.Many2one('hr.employee', readonly=True)
    is_added_qty = fields.Boolean()