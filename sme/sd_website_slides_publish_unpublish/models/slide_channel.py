
from odoo import models, fields,api


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    content_publish_status = fields.Selection(string='Publish_status', selection=[
                ('published', 'Published'),
                ('unpublished', 'UnPublished'),
                ('both', 'Both'), ], default='both')

    @api.onchange('slide_ids', 'slide_ids.is_published')
    def onchange_default_published(self):
        for rec in self:
            if any(not slide.is_published for slide in rec.slide_ids):
                rec.content_publish_status = 'both'

    def website_publish(self):
        self.write({'is_published': True})

    def website_unpublish(self):
        self.write({'is_published': False})

    def publish_content(self):
        if self.slide_ids:
            for rec in self.slide_ids:
                if rec.is_published is False:
                    rec.is_published = True
            self.content_publish_status = 'published'

    def unpublish_content(self):
        if self.slide_ids:
            for rec in self.slide_ids:
                if rec.is_published is True:
                    rec.is_published = False
            self.content_publish_status = 'unpublished'
