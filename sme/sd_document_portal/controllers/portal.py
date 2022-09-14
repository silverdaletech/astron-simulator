
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request
import base64

from odoo.addons.portal.controllers import portal

from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager

today = fields.Date.from_string(fields.Date.today())


class PortalDocument(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # User Partner
        partner = request.env.user.partner_id.sudo()
        # Domain for active share documents
        domain = ['|', ('date_deadline', '>=', today), ('date_deadline', '=', False)]
        share_count = request.env['documents.share'].search(domain)
        # Get all documents from share links
        documents_ids = share_count.document_ids

        # Documents object
        documents = request.env['documents.document'].sudo()
        # Count documents where user partner is set
        doc_domain = [('id', 'in', documents_ids.ids), ('partner_id', '=', partner.id)]
        self_doc_ids = documents.search(doc_domain)

        share_with_partner_ids = request.env['res.partner'].sudo()
        if partner.company_type == 'company':
            share_with_partner_ids = partner.child_ids
        elif partner.company_type == 'person' and partner.parent_id:
            share_with_partner_ids = partner.parent_id.child_ids + partner.parent_id

        shared_docs_domain = [('id', 'in', documents_ids.ids), ('partner_id', '=', share_with_partner_ids.ids), ('share_with_company', '=', True)]

        shared_doc_ids = documents.search(shared_docs_domain)

        documents_count = self_doc_ids | shared_doc_ids
        values['documents_count'] = len(documents_count)
        return values

    @http.route(['/my/documents', '/my/documents/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):

        partner = request.env.user.partner_id.sudo()
        # Get all active share link
        domain = ['|', ('date_deadline', '>=', today), ('date_deadline', '=', False)]
        share_count = request.env['documents.share'].search(domain)
        documents_ids = share_count.document_ids
        
        # Documents object
        documents = request.env['documents.document'].sudo()
        # Count documents where user partner is set
        doc_domain = [('id', 'in', documents_ids.ids), ('partner_id', '=', partner.id)]
        self_doc_ids = documents.search(doc_domain)

        share_with_partner_ids = request.env['res.partner'].sudo()
        if partner.company_type == 'company':
            share_with_partner_ids = partner.child_ids
        elif partner.company_type == 'person' and partner.parent_id:
            share_with_partner_ids = partner.parent_id.child_ids + partner.parent_id

        shared_docs_domain = [('id', 'in', documents_ids.ids), ('partner_id', '=', share_with_partner_ids.ids),
                              ('share_with_company', '=', True)]

        shared_doc_ids = documents.search(shared_docs_domain)
        shared_document_ids = self_doc_ids | shared_doc_ids
        documents = len(shared_document_ids)

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'

        documents_count = documents
        # pager
        pager = portal_pager(
            url="/my/documents",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=documents_count,
            page=page,
            step=10
        )

        documents = request.env['documents.document'].sudo().search([('id', 'in', shared_document_ids.ids)], limit=10, offset=pager['offset'])

        value = {
            'date': date_begin,
            'page_name': 'documents',
            'pager': pager,
            'default_url': '/my/documents',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'documents': documents,
        }
        return request.render("sd_document_portal.portal_my_documents", value)

    @http.route(['/upload/document'], type='http', auth="user", csrf=False)
    def portal_upload_document(self, access_token=None, **kw):
        """
            Upload user document
        """
        rec = request.redirect('/my/documents')
        
        ufile = kw.get('ufile').read()
        folder_id = False
        folder_id = request.env.company.portal_folder.id or False
        if not folder_id:
            folder_id = request.env.ref('sd_document_portal.documents_portal_folder').id
        vals = {
            'name': kw.get('ufile').filename, 
            'folder_id': folder_id,
            'partner_id': request.env.user.partner_id.id,
            'share_document': True
            }
        document = request.env['documents.document'].sudo().create(vals)
        vals = {
            'name': kw.get('ufile').filename, 
            'datas': base64.b64encode(ufile),
            'res_model': 'documents.document',
            'res_id': document.id
        }
        attachment = request.env['ir.attachment'].sudo().create(vals)
        document_share = {
            'name': "{} - {}".format(request.env.user.name, document.name),
            'owner_id': request.env.uid,
            'folder_id': folder_id,
            'type': 'ids',
            'document_ids': [(4, document.id)],
        }
        document_share_link = request.env['documents.share'].sudo().create(document_share)
        return rec
