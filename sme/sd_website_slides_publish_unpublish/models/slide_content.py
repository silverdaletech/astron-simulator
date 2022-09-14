
from odoo import models, fields


class SlideContent(models.Model):
    _inherit = 'slide.slide'

    def website_content_publish(self):
        self.write({'is_published': True})

    def website_content_unpublish(self):
        self.write({'is_published': False})
