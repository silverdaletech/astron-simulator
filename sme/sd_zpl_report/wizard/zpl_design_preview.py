# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ZplDesignPreview(models.TransientModel):
    """
    this model is for displaying the zpl view to user after customizing the label.
    """
    _name = 'zpl.design.preview'
    _description = 'ZPL Design Preview'

    image = fields.Binary(string="Image", attachment=True)
    density_choosen = fields.Integer(reaonly=True)