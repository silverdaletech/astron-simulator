
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AuditMasterData(models.Model):
    _name = 'audit.master.data'
    _description = 'Audi Master Data'

    name = fields.Many2one('ir.model', string="Model")
    domain_line = fields.One2many('master.data.domain', 'master_data_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.onchange('name')
    def _onchange_name(self):
        for rec in self:
            rec.domain_line = False


class MasterDataDomain(models.Model):
    _name = 'master.data.domain'
    _description = 'Master Data Domain'

    name = fields.Char('Name', required=True)
    field_id = fields.Many2one('ir.model.fields')
    domain = fields.Char(default='[]', required=True)
    master_data_id = fields.Many2one('audit.master.data')
    model_id = fields.Char(related='master_data_id.name.model')


class DuplicateDataCount(models.Model):
    _name = 'duplicate.data.count'
    _description = 'Duplicate Data Count'

    name = fields.Many2one('ir.model', string="Model")
    duplicate_data_line = fields.Many2many('ir.model.fields')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.onchange('name')
    def _onchange_name(self):
        for rec in self:
            rec.duplicate_data_line = False
