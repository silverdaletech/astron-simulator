# -*- coding: utf-8 -*-


from odoo import api, fields, models, _, SUPERUSER_ID


class CustomResponseMessage(models.TransientModel):
    _name = 'custom.response.message.wizard'
    _description = 'Custom Response Message'

    message = fields.Html("Response", readonly=True)
