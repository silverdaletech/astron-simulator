# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ZplDesignHistory(models.Model):
    """ This model will contain all the previous (ZPL) label templates whenever user makes changes in current template.
        containing previous templates in this model is for saving the history of templates, if users want to UNDO
        changes, then he/she will get his/her previous (ZPL) label design back.
    """
    _name = 'zpl.design.history'
    _description = 'zpl design history'

    name = fields.Char(string="Name")
    template = fields.Text(string="Template")
    is_selected = fields.Boolean(string="Selected")
    zpl_design_id = fields.Many2one('zpl.label.design')
