from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Lead',
        required=False)

    @api.model
    def create(self, values):
        if 'lead_id' in values:
            lead = self.env['crm.lead']
            lead_id = lead.sudo().search([('id', '=', values.get('lead_id', False))])
            if lead_id and lead_id.account_analytic_id:
                account = lead_id.account_analytic_id.id
            values['account_id'] = account
        lead = super(AccountAnalyticLine, self).create(values)
        return lead
