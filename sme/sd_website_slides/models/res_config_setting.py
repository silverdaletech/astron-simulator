# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_vimeo_video = fields.Boolean(
        string='Vimeo Videos - eLearning Platform')
    module_sd_website_slides_publish_unpublish = fields.Boolean(
        string='Silverdale eLearning Publish/UnPublish')
    module_sd_invite_multiple_attendees = fields.Boolean(
        string='Invite multiple attendees')
    module_sd_website_slides_video = fields.Boolean(
        string='eLearning Document Videos')
