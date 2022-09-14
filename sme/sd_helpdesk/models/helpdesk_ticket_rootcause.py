# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicketRootCause(models.Model):
    _name = 'ticket.rootcause'
    _description = 'Ticket RootCause'
    _order = 'sequence'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence')
