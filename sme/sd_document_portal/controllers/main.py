# -*- coding: utf-8 -*-

import base64
import zipfile
import io
import json
import logging
import os
from contextlib import ExitStack

from odoo import http
from odoo.addons.documents.controllers.main import ShareRoute
from odoo.exceptions import AccessError
from odoo.http import request, content_disposition
from odoo.tools.translate import _
from odoo.tools import image_process


class SDShareRoute(ShareRoute):

    @http.route()
    def share_portal(self, share_id=None, token=None):
        """
        Add pdf_datas for pdf preview in qcontext if the number of document is 1.
        """
        res = super(SDShareRoute, self).share_portal(share_id, token)
        share = http.request.env['documents.share'].sudo().browse(share_id)
        available_documents = share._get_documents_and_check_access(token, operation='read')
        if len(available_documents) == 1:
            res.qcontext['pdf_datas'] = available_documents.attachment_id.sudo().datas.decode()
        return res
