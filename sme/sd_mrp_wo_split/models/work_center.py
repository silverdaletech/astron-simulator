from odoo import fields, models, api, _


class WorkCenter(models.Model):
    _inherit = 'mrp.workcenter'

    user_id = fields.Many2one('res.users')