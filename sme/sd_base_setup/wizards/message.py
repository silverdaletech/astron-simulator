from odoo import api, fields, models, _, SUPERUSER_ID
import requests
import json


class SdMessageWizard(models.TransientModel):
    _name = 'sd.message.wizard'
    _description = 'Silverdale Message'

    def _get_message(self):
        return self._context['message']

    message = fields.Html("Response", default=_get_message, readonly=True)