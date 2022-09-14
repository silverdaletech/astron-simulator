# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError

class ZplLabelSize(models.Model):
    """
    this model is for creating the size of zpl label.
    """
    _name = 'zpl.label.size'
    _description = 'zpl label size'

    name = fields.Char(string="Name", required=True, default="4X6")
    height = fields.Char('Height', required=True, default=6, Required=True)
    width = fields.Char('Width', required=True, default=4, Required=True)
    unit_of_measure = fields.Selection([('mm', 'MM'),
                                        ('inches', 'Inches'),
                                        ], string='Unit of Measure', default='inches')
    density = fields.Selection([('6', '6 dpmnn (152 dpi)'),
                                ('8', '8 dpmnn (203 dpi)'),
                                ('12', '12 dpmnn (300 dpi)'),
                                ('24', '24 dpmnn (600 dpi)')
                                ], string='Density', required="1", default='8')


    @api.constrains('height', 'width')
    def height_is_integer(self):
        """
        thid method will allow user only enter float or integer values for width and height of zpl label size,
        not only that it will also allow user to enter values only
        in the range of 0.001 to 15.0 for both width and height.
        """
        height_flag = 0
        if self.height:
            try:
                height = float(self.height)
                if height:
                    if height >= 0.001 and height <= 15.0:
                        height_flag = 1
            except:
                raise UserError('Sorry! Only Integer or Float Values are allowed For ZPL Label Height.')
            if height_flag == 0:
                raise UserError("Sorry given range is Invalid, the Valid range is (0.001 inches To 15.0 inches) for ZPL Label Height.")
        width_flag = 0
        if self.width:
            try:
                width = float(self.width)
                if width:
                    if width >= 0.001 and width <= 15.0:
                        width_flag = 1
            except:
                raise UserError('Sorry! Only Integer or Float Values are allowed For ZPL Label Width.')
            if width_flag == 0:
                raise UserError("Sorry given range is Invalid, the Valid range is (0.001 inches To 15.0 inches) for ZPL Label Width.")
