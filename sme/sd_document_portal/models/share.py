# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class DocumentShare(models.Model):
    _inherit = 'documents.share'

    @api.model
    def open_share_popup(self, vals):
        """
        Check if no_popup is True in vals then do not show the wizard,
        create record in documents.share model and return false
        else continue the normal flow
        """
        values = {}
        if vals.get('no_popup', False):

            values.update({
                'name': 'Auto Generated',
                'owner_id': self.env.uid,
                'folder_id': vals.get('folder_id'),
                'tag_ids': vals.get('tag_ids'),
                'type': vals.get('type', 'domain'),
                'domain': vals.get('domain') if vals.get('type', 'domain') == 'domain' else False,
                'document_ids': vals.get('document_ids', False),
                'date_deadline': self.env.company.shared_link_default_deadline
            })

            today = fields.Date.from_string(fields.Date.today())

            # If at least one live link already exists then do not create another link.
            live_link_exists = self.sudo().search(['|', ('date_deadline', '>', today),
                                                   ('date_deadline', '=', False),
                                                   ('document_ids', 'in', vals.get('doc_ids', []))], limit=1)
            if not live_link_exists:
                self.sudo().create(values)

            return False
        else:
            return super(DocumentShare, self).open_share_popup(vals)

    @api.model
    def unlink_live_shared_link(self, vals):
        """
        Unlink already existing live link if button is unchecked.
        """
        if vals:
            today = fields.Date.from_string(fields.Date.today())
            live_link_exists = self.sudo().search(['|', ('date_deadline', '>', today),
                                                   ('date_deadline', '=', False),
                                                   ('document_ids', 'in', vals)], limit=1)
            if live_link_exists:
                live_link_exists.sudo().unlink()
