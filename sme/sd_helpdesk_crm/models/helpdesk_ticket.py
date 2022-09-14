# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HelpdeskTicketInherit(models.Model):
    _inherit = "helpdesk.ticket"

    lead_ids = fields.One2many('crm.lead', 'ticket_id', string='Opportunities')
    leads_count = fields.Integer(compute="_compute_leads_count")

    @api.depends('lead_ids')
    def _compute_leads_count(self):
        for ticket in self:
            ticket.leads_count = len(ticket.lead_ids)

    def action_open_leads_view(self):
        if len(self.lead_ids) > 1:
            views = 'tree,form'
            res_id = False
            domain = "[('id', 'in', %s)]" % self.lead_ids.ids
        else:
            views = 'form'
            res_id = self.lead_ids.id
            domain = False
        return {
            'name': _('Opportunities'),
            'view_mode': views,
            'res_model': 'crm.lead',
            'domain': domain,
            'view_id': False,
            'res_id': res_id,
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_create_opportunity(self):
        view = self.env.ref('crm.crm_lead_view_form')

        return {
            'name': _('New Opportunity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': False,
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_ticket_id': self.id,
                'default_name': self.name,
                'default_description': self.description,
            }
        }





