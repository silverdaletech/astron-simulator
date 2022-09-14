from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CRMPriceRole(models.Model):
    _name = 'crm.price.role'
    _description = 'CRM Price Role'

    name = fields.Many2one(string="User Roles",
                comodel_name='res.groups',
                domain=[('category_id', 'like', 'Sale')],
                required="1")
    allow_percentage = fields.Float()

    #--------------------------------------------------
    # Constraints
    #--------------------------------------------------

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'User Roles must be unique.')
    ]

    @api.constrains('allow_percentage')
    def _check_allow_percentage(self):
        for record in self:
            if record.allow_percentage < 1:
                raise ValidationError("Percentage should be greater then 0")
            elif record.allow_percentage > 100:
                raise ValidationError("Percentage should not greater then to 100")