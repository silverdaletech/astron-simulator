# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import io
import re
import requests
import PyPDF2
import json

from dateutil.relativedelta import relativedelta
from PIL import Image
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, AccessError
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for
from odoo.tools import html2plaintext, sql


class Channel(models.Model):
    _inherit = 'slide.channel'

    nbr_doc_video = fields.Integer("Document Video", compute='_compute_slides_statistics', store=True)


class Slide(models.Model):
    _inherit = 'slide.slide'

    slide_type = fields.Selection(
                        selection_add=[('doc_video', 'Document Video')],
                        ondelete={'doc_video': 'set default'}
                        )
    documents_document_id = fields.Many2one('documents.document', string='Document',
                                  domain=[('attachment_id.mimetype', '=', 'video/mp4')]
                                  )
    nbr_doc_video = fields.Integer("Document Video", compute='_compute_slides_statistics', store=True)

    @api.onchange('documents_document_id')
    def _on_change_documents_document_id(self):
        if self.document_id:
            self.slide_type = 'doc_video'

    def get_binary_document_video(self):
        """
        Called from _renderSlide function in js to get string of binary video from document.
        """
        datas = ''
        if self.documents_document_id.attachment_id:
            datas = self.documents_document_id.sudo().attachment_id.datas.decode()
        return datas
