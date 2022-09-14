# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError
import base64
import io
import logging
from PIL import Image
_logger = logging.getLogger(__name__)
import re
import zpl

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

class ZplCustomContent(models.TransientModel):
    """
    this model is for adding more content inside zpl label report. this way user can customize the label.
    """
    _name = 'zpl.custom.content'
    _description = 'ZPL Custom Content'

    x_origin = fields.Float(string="X-Origin")
    y_origin = fields.Float(string="Y-Origin")
    model_id = fields.Many2one('ir.model', string="Model")
    field_id = fields.Many2one('ir.model.fields', string="Field")
    char_height = fields.Integer(string="Character Height", default=3)
    char_width = fields.Integer(string="Character Width", default=3)
    line_width = fields.Integer(string="Line Width", default=50)
    justification = fields.Selection([('L', 'Left'),
                                      ('C', 'Center'),
                                      ('R', 'Right')
                                      ], string='Horizontal Alignment', default='L')
    content_type = fields.Selection([('custom_content', 'Add Custom Text'),
                                     ('field', 'Add Field'),
                                     ('line', 'Add Line'),
                                     ('rectangle', 'Add Rectangle'),
                                     ('circle', 'Add Circle'),
                                     ('barcode', 'Add Barcode'),
                                     ('qr', 'Add QR Code'),
                                     ('gs1', 'Add GS1 Barcode'),
                                     ('image_logo', 'Add Image/logo')
                                    ], string='Content Type', default='custom_content', required=True)
    line_length = fields.Integer(string="Line Length", default=40)
    line_type = fields.Selection([('V', 'Vertical'),
                                  ('H', 'Horizontal'),
                                  ('D', 'Diagonal')
                                  ], string='Line Type', default='H', required=True)
    circle_diameter = fields.Integer(string="Diameter", default=50)
    thickness = fields.Integer(string="Thickness", default=3)
    color = fields.Selection([('B', 'Black'),
                              ('W', 'White')
                              ], string='Color', default='B', required=True)
    orientation = fields.Selection([('R', 'right-leaning'),
                                    ('L', 'left-leaning')
                                    ], string='Orientation', default='R', required=True)
    diagonal_height = fields.Integer(string="Diagonal Height", default=20)
    diagonal_width = fields.Integer(string="Diagonal Width", default=20)
    barcode_size = fields.Integer(string="Bar Height", default=30)
    barcode_type = fields.Selection([('U', 'UPC codes'),
                                      ('E', 'EAN codes'),
                                      ('C', 'Codabar'),
                                      ('3', 'Code 39'),
                                      ], string='Barcode Type', default='C', required=True)
    barcode_text_position = fields.Selection([('Y', 'Above'),
                                              ('N', 'Below')
                                              ], string='Text Position', help="If 'Above' is selected then it will add human readable above the barcode, if 'Below' is selected then it will add human readable below the barcode,")
    text_in_multiline = fields.Integer(string="Multiple Lines", default=10)
    qr_code_size = fields.Integer(string="QR-Code Size", default=5)
    custom_text = fields.Char(string="Custom Text")
    image_width = fields.Integer(string="Image Width", default=30)
    image_height = fields.Integer(string="Image Height", default=30)
    image = fields.Binary(string="Image", attachment=True)
    model_name = fields.Char(related='model_id.model', string="Model Name", store=True)
    field_chain = fields.Char(string="Field", store=True)
    gs1_barcode_rule = fields.Selection([('rule1', 'Product+Quantity+Lot'), ('rule2', 'Product+Lot+Quantity'),
                                         ('rule3', 'Quantity+Product+Lot'), ('rule4', 'Quantity+Lot+Product'),
                                         ('rule5', 'Lot+Product+Quantity'), ('rule6', 'Lot+Quantity+Product'),
                                        ], string='GS1 Barcode Rule', default='rule1', required=True)
    product_barcode = fields.Char(string="Product Barcode")
    product_quantity = fields.Char(string="Quantity")
    product_lot = fields.Char(string="Lot Number")
    gs1_barcode_size = fields.Integer(string="GS1 Barcode Size", default=50)

    @api.onchange('field_chain')
    def _onchange_field_chain(self):
        for rec in self:
            if rec.field_chain:
                if '&' in rec.field_chain:
                    raise UserError("Sorry! You Can't Select MUltiple field Chain.")

    def action_add_field(self):
        """
        this method will add the New Content in the ZPL Label Template.
        """
        # field = self.field_id.name
        field = self.field_chain
        if field:
            field = field.split('"')[1]
        tty = self.env['ir.model.fields'].search([('model', '=', self.model_name), ('name', '=', field)])
        field_type = tty.ttype
        if field_type == 'many2one':
            model = self.env['ir.model'].search([('model', '=', self.field_id.relation)])
            field = f'{self.field_id.name}{"."+model._rec_name}'
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        temp = rec.content
        index_from = temp.rindex('^XA')
        temp_first_part = temp[:index_from]
        index_to = temp.rindex('^XZ')
        index_to = index_to + 3
        temp_last_part = temp[index_to:]
        temp = temp[index_from:index_to]
        temp = temp.replace('^XZ', '')
        # l = ZplConverter(100, 100)
        l = zpl.Label(100, 100)
        l.code = temp + "\n"
        x_axis = (self.x_origin)/12
        y_axis = (self.y_origin)/12
        l.origin(x_axis, y_axis)
        data = False
        if field:

            if field_type == 'monetary':
                data = """<t t-esc="doc.""" + field + """" t-options='{"widget": "float", "precision": 2}'/>"""
            else:
                data = """<t t-esc="doc.""" + field + """"/>"""

        if self.content_type == 'custom_content':
            l.write_text(self.custom_text + "\n", char_height=self.char_height, char_width=self.char_width,
                         line_width=self.line_width, justification=self.justification)
        elif self.content_type == 'field':
            if data:
                l.write_text(data + "\n", char_height=self.char_height, char_width=self.char_width,
                             line_width=self.line_width, justification=self.justification, max_line=self.text_in_multiline)
            else:
                raise UserError("Please Select a field")
        elif self.content_type == 'line':
            x_axis = x_axis * 12
            y_axis = y_axis * 12
            if self.line_type == 'H':
                l.code = temp + "\n" + "^FO" + str(x_axis) + "," + str(y_axis) + "^GB" + str(
                    self.line_length) + ",5," + str(self.thickness) + "," + str(self.color) + "^FS" + "\n"
            elif self.line_type == 'V':
                l.code = temp + "\n" + "^FO" + str(x_axis) + "," + str(y_axis) + "^GB5," + str(
                    self.line_length) + "," + str(self.thickness) + "," + str(self.color) + "^FS" + "\n"
                pass
            elif self.line_type == 'D':
                l.code = temp + "\n" + "^FO" + str(x_axis) + "," + str(y_axis) + "^GD" + str(
                    self.diagonal_width) + "," + str(self.diagonal_height) + "," + str(self.thickness) + "," + str(
                    self.color) + "," + str(self.orientation) + "^FS" + "\n"
            else:
                raise UserError("Please Select Line Type")
        elif self.content_type == 'rectangle':
            x_axis = x_axis * 12
            y_axis = y_axis * 12
            l.code = temp + "\n" + "^FO" + str(x_axis) + "," + str(y_axis) + "^GB" + str(
                self.diagonal_width) + "," + str(self.diagonal_height) + "," + str(self.thickness) + "," + str(
                self.color) + "^FS" + "\n"
        elif self.content_type == 'circle':
            x_axis = x_axis * 12
            y_axis = y_axis * 12
            l.code = temp+"\n"+"^FO"+str(x_axis)+","+str(y_axis)+"^GC"+str(self.circle_diameter)+","+str(
                self.thickness)+","+str(self.color)+"^FS"+"\n"
        elif self.content_type == 'barcode':
            if data:
                if self.barcode_text_position:
                    l.write_barcode(
                        self.barcode_size, self.barcode_type, 'Y', 'Y', 'Y', self.barcode_text_position, 'Y', 'N')
                else:
                    l.write_barcode(self.barcode_size, self.barcode_type, 'N', 'N', 'N')
                l.write_text(data + "\n")
            else:
                raise UserError("Please Select a Field")
        elif self.content_type == 'qr':
            if data:
                l.write_barcode(7, 'Q', 'N', 'N', 7, 'Q', self.qr_code_size)
                l.write_text("QA," + data + "\n")
            else:
                raise UserError("Please Select a Field")
        elif self.content_type == 'gs1':
            product = self.product_barcode
            quantity = self.product_quantity
            lot = self.product_lot

            if self.gs1_barcode_rule == 'rule2':
                gs1code = "01" + product + str(chr(92)) + "x1D10" + lot + str(chr(92)) + "x1D30" + quantity
            elif self.gs1_barcode_rule == 'rule3':
                gs1code = "30" + quantity + str(chr(92)) + "x1D01" + product + str(chr(92)) + "x1D10" + lot
            elif self.gs1_barcode_rule == 'rule4':
                gs1code = "30" + quantity + str(chr(92)) + "x1D10" + lot + str(chr(92)) + "x1D01" + product
            elif self.gs1_barcode_rule == 'rule5':
                gs1code = "10" + lot + str(chr(92)) + "x1D01" + product + str(chr(92)) + "x1D30" + quantity
            elif self.gs1_barcode_rule == 'rule6':
                gs1code = "10" + lot + str(chr(92)) + "x1D30" + quantity + str(chr(92)) + "x1D01" + product
            else:
                gs1code = "01" + product + str(chr(92)) + "x1D30" + quantity + str(chr(92)) + "x1D10" + lot

            l.write_barcode(self.gs1_barcode_size, 'C', 'N', 'N', 'N')
            l.write_text(gs1code + "\n")

        elif self.content_type == 'image_logo':
            img = self.image
            l.write_graphic(Image.open(io.BytesIO(base64.b64decode(img))), self.image_width, self.image_height)

        l.endorigin()
        zpl_dump = l.dumpZPL()
        zpl_dump = zpl_dump.replace("^XZ", "\n^XZ")
        temp = temp_first_part + zpl_dump + "\n" +temp_last_part
        rec.content = temp
        rec.report_template_id.arch_base = temp
        temp = temp.replace(""" t-options='{"widget": "float", "precision": 2}'""", "")
        rec.content_buffer = temp

        allhistory = self.env['zpl.design.history'].search([('zpl_design_id', '=', rec._origin.id)], order='id desc')
        history_ids = allhistory.ids
        first_history_flag = 0

        for hist in allhistory:
            if first_history_flag == 0:
                history = hist
                first_history_flag = 1
            hist.is_selected = False
        try:
            hist = history.name
            hist = "Template-" + str(int(hist.split("-")[1]) + 1)
        except Exception as e:
            hist = "Template-1"
        new_hist = history.create(
            {'name': hist, 'template': rec.content, 'zpl_design_id': rec._origin.id, 'is_selected': True})

        new_hist_id = new_hist.id
        if rec.undo_redo:
            undo_redo = rec.undo_redo.strip()
            all_chars_ids = undo_redo.split(" ")
            new_char_ids = []
            for char_ids in all_chars_ids:
                new_char_ids.append(int(char_ids))
            last_hist_id = new_char_ids[-1]
            new_char_ids.insert(0, last_hist_id)
            new_char_ids[-1] = new_hist_id
            elements_of_ids = ""
            for id in new_char_ids:
                elements_of_ids = elements_of_ids + str(id) + " "
            rec.undo_redo = elements_of_ids
        else:
            last_one = history_ids[-1]
            lsts = ""
            for hs in history_ids:
                if last_one != hs:
                    lsts = lsts + str(hs) + " "
            rec.undo_redo = str(last_one) + " " + lsts + str(new_hist_id)
