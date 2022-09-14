# -*- coding: utf-8 -*-

import base64
import requests
from odoo import api, fields, models, _
from werkzeug import urls
from odoo.exceptions import UserError

class Channel(models.Model):
    """ A channel is a container of slides. """
    _inherit = 'slide.channel'
    _name = 'slide.channel'

    nbr_vimeovideo = fields.Integer('Vimeo Videos', compute='_compute_slides_statistics', store=True)


class Slide(models.Model):
    _inherit = 'slide.slide'
    _name = 'slide.slide'

    # content
    external_url = fields.Char(string="Vimeo Video URL")
    slide_type = fields.Selection(selection_add=[
        ('vimeovideo', 'Vimeo Video')],
        ondelete={'vimeovideo': 'set default'})
    nbr_vimeovideo = fields.Integer('Vimeo Video', compute='_compute_slides_statistics', store=True)

    @api.depends('document_id', 'slide_type', 'mime_type', 'external_url')
    def _compute_embed_code(self):
        res = super(Slide, self)._compute_embed_code()
        for record in self:
            if record.slide_type == 'vimeovideo':
                vimeo_parse = self.parse_video_url(record.external_url)
                content_url = 'https://player.vimeo.com/video/' + vimeo_parse[1]
                record.embed_code = '<iframe class="vimeoVideo" src="' + content_url + '" allowfullscreen="allowfullscreen" mozallowfullscreen="mozallowfullscreen" msallowfullscreen="msallowfullscreen" oallowfullscreen="oallowfullscreen" webkitallowfullscreen="webkitallowfullscreen"></iframe>'

    def parse_video_url(self, url):
        url_obj = urls.url_parse(url)
        if url_obj.ascii_host == 'vimeo.com':
            if url_obj.path:
                response = requests.get("https://vimeo.com/api/oembed.json?url=" + url)
            else:
                response = False
            return ('vimeo', url_obj.path[1:] if url_obj.path else False, response)

    @api.onchange('slide_type', 'external_url')
    def onchange_slide_type(self):
        for record in self:
            if record.slide_type == 'vimeovideo' and record.external_url:
                parse_url = self.parse_video_url(record.external_url)
                if parse_url and parse_url[2]:
                    jsonResponse = parse_url[2].json()
                    if 'duration' in jsonResponse:
                        record.completion_time = jsonResponse['duration']/3600
                    else:
                        record.completion_time = 0
                    if 'title' in jsonResponse:
                        record.name = jsonResponse['title']
                    else:
                        record.name = 'Video with security restrictions (embed in this domain for example). Verify in your vimeo account or contact with video owner.'
                    if 'description' in jsonResponse:
                        record.description = jsonResponse['description']
                    else:
                        record.description = 'Video with security restrictions (embed in this domain for example). Verify in your vimeo account or contact with video owner.'
                    if 'thumbnail_url' in jsonResponse:
                        record.image_1920 = base64.b64encode(requests.get(jsonResponse['thumbnail_url']).content)
                    else:
                        record.image_1920 = False
                else:
                    raise UserError(_("Unknown document"))