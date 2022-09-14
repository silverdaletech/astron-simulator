# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from bs4 import BeautifulSoup
from lxml import etree
from odoo import _, api, fields, models, tools, Command


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_for_help = fields.Boolean()
    url_link = fields.Char()

    @api.onchange('subject', 'url_link')
    def sd_onchange_subject(self):
        if self.body and self.subject and self.is_for_help:
            soup = BeautifulSoup(self.body, 'html.parser')
            soup.find(id="query").string = self.subject
            soup.find(id="url_link").string = self.url_link
            self.body = soup

    @api.model
    def get_help_default_data(self):
        recipient_id = self.env['res.partner'].sudo().search([('email', '=', 'help@silverdaletech.com')], limit=1)
        template_id = self.env.ref('sd_base_setup.mail_template_get_help')
        data = {
            'recipient_id': recipient_id.id or False,
            'template_id': template_id.id
        }
        return data

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MailComposer, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'mail.message')])
        doc = etree.XML(res['arch'])
        if self._context.get('default_is_for_help', False):
            doc.xpath("//field[@name='template_id']")[0].set('domain', f"[('model_id', '=', {model_id.id})]")

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
