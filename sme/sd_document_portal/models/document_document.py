from odoo import models, api, fields, _ 


class Document(models.Model):
    _inherit = 'documents.document'

    share_document = fields.Boolean('Share Doc?')
    share_with_company = fields.Boolean('With Company', help="Share this document across the company "
                                                             "if checked else just with individual user.")

    def get_portal_link(self):
        """
        Return shareable link.
        """
        documents_share = self.env['documents.share'].search([
            ('document_ids', 'in', self.id), ('date_deadline', '=', False)], limit=1)
        if documents_share:
            return documents_share
        
        today = fields.Date.from_string(fields.Date.today())
        documents_share = self.env['documents.share'].search([
            ('document_ids', 'in', self.id), ('date_deadline', '>=', today)], limit=1)
        if documents_share:
            return documents_share

        return False

    def change_folder_in_shared_links(self, kw):
        """
        RPC Call from JS
        Change the folder in all shared links of this document/s, if document/s folder is changed
        """
        share_link_ids = self.env['documents.share'].sudo().search([('document_ids', 'in', self.ids)])
        for link in share_link_ids:
            link.folder_id = kw.get('folder_id', False)
