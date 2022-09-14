# -*- coding: utf-8 -*-
from odoo import models, fields


class AuditAddonsList(models.Model):
    _name = 'audit.addons.list'
    _description = 'Audit Addons List'

    name = fields.Char('Name', required=1)
