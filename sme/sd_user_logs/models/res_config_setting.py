from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    enforce_time_interval = fields.Boolean(
        string='Enforce Maximum Time Between Logins')
    # interval
    interval_number = fields.Integer(string='Maximum Time Between Login', default=1)
    interval_type = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')], string='Interval Type',
        default='months',)

    @api.constrains('interval_number', 'interval_type')
    def _check_values(self):
        if self.interval_number == 0 or self.interval_type is False:
            raise ValidationError(_('Time Interval should not be zero or empty.'))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enforce_time_interval = fields.Boolean(
        string='Enforce Maximum Time Between Logins', related="company_id.enforce_time_interval", readonly=False)
    # interval
    interval_number = fields.Integer(string='Maximum Time Between Login', related="company_id.interval_number", readonly=False)
    interval_type = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')], string='Interval Type', related="company_id.interval_type", readonly=False)
