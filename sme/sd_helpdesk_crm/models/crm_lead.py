# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = "crm.lead"

    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")

    def action_open_tickets_view(self):
        return {
            'name': _('Ticket'),
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'view_id': False,
            'res_id': self.ticket_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

