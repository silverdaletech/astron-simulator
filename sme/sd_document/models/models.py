# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DocumentInherit(models.Model):
    _inherit = 'documents.document'

    model_id = fields.Many2one(comodel_name="ir.model", string="Model", required=False, )
    model_record_id = fields.Integer(string="Record ID", required=False, )

    def attach_file_with_record(self, rec_model, rec_id):
        model = self.env['ir.model'].browse(rec_model)
        for rec in self.filtered(lambda d: d.type == 'binary'):
            record = self.env[model.model].browse(rec_id)
            attachment = self.env['ir.attachment'].create({
                'name': rec.attachment_id.name or 'new',
                'type': rec.attachment_id.type,
                'datas': rec.attachment_id.datas,
                'res_model': model.model,
                'res_id': record.id,
            })
        return model.model
