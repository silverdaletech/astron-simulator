# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, AccessError
import random
import string
import base64
import requests
import re

class ZplLabelDesign(models.Model):
    """
        This is the model in which user will create new (ZPL) Label,
        and after creation it can be customized.
    """
    _name = 'zpl.label.design'
    _description = 'zpl label design'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    size_id = fields.Many2one('zpl.label.size', string="Size")
    show_in = fields.Boolean(string="Show in", help="if true, report will be visible in print menue")
    template_id = fields.Many2one('ir.ui.view', string="Design Template", domain="[('type', '=', 'qweb')]")
    selected_model_id = fields.Many2one('ir.model', string="Use In", ondelete='cascade')
    report_action_id = fields.Many2one('ir.actions.report', string="Report Action")
    report_model_data_id = fields.Many2one('ir.model.data', string="Model Data ")
    report_template_id = fields.Many2one('ir.ui.view', string="ZPL Report Template", domain="[('type', '=', 'qweb')]")
    active = fields.Boolean(string="Active", default=True)
    default_label = fields.Boolean(string="Default Label", default=False)
    content = fields.Text(string="ZPL Template")
    old_content = fields.Text()
    content_buffer = fields.Text(string="ZPL Buffer")
    hidden_template = fields.Text()
    field_id = fields.Many2one('ir.model.fields', string="Field", store=False )
    place_holder = fields.Char('Placeholder', store=False)
    zpl_content = fields.Html(string='ZPL Label Template', compute='_compute_zpl_content')
    image = fields.Binary(string="Image", attachment=True)
    zpl_history_ids = fields.One2many('zpl.design.history', 'zpl_design_id', string="History")
    is_archive = fields.Boolean(compute="_compute_is_archive")
    dpi = fields.Char(compute="_compute_dpi")
    is_undo_redo = fields.Boolean(compute="_compute_is_undo_redo")
    is_redo = fields.Boolean()
    is_undo = fields.Boolean()
    undo_redo = fields.Char()

    @api.depends('undo_redo')
    def _compute_is_undo_redo(self):
        for rec in self:
            if rec.undo_redo:
                undo_redo = rec.undo_redo.strip()
                undo_redo = undo_redo.split(" ")
                if len(undo_redo)>1:
                    rec.is_undo_redo = True
                else:
                    rec.is_undo_redo = False
            else:
                rec.is_undo_redo = False

    @api.depends('size_id', 'size_id.width', 'size_id.density')
    def _compute_dpi(self):
        for rec in self:
            rec.dpi = ""
            if rec.size_id:
                # dens = dict(rec.size_id._fields['density'].selection).get(rec.size_id.density).split()[0].split("(")[1]
                density = int(dict(rec.size_id._fields['density'].selection).get(rec.size_id.density).split("(")[1].split()[0])
                width = float(rec.size_id.width)
                rec.dpi = """
                             ^MMT
                             ^PW""" + str(round(density * width)) + """
                             ^LL0""" + str(density) + """
                             ^LS0"""
            if rec.content:
                content_part = rec.content
                index_from_xa = content_part.rindex('^XA')
                part_a = content_part[:index_from_xa+3]
                part_c = content_part[index_from_xa+3:]
                if "^LS0" in content_part:
                    index_from_lso = content_part.rindex('^LS0')
                    part_c = content_part[index_from_lso+4:]
                rec.content = part_a + rec.dpi + part_c

    def unlink(self):
        for rec in self:
            rec.report_action_id.unlink()
            rec.report_template_id.unlink()
            rec.report_model_data_id.unlink()
        return super(ZplLabelDesign, self).unlink()

    @api.depends('active')
    def _compute_is_archive(self):
        for rec in self:
            if rec.active:
                if rec.show_in:
                    rec.report_action_id.create_action()
            else:
                rec.report_action_id.unlink_action()
            rec.is_archive = rec.active

    @api.model
    def create(self, vals_list):
        """
        create method is inherited to create a default zpl label report for user on new record creation.
        """
        res = super(ZplLabelDesign, self).create(vals_list)
        self.action_create_default_template(res)
        return res

    def action_create_default_template(self, res):
        """
        this method will be executed when a new record is created for zpl label report.
        and what this method does is,
        it will create a default zpl label template report for selected model.
        """

        if self.default_label:

            temp = """
                        ^XA 
                       
                            ^FO0,25^A0,35,25^FB500,1,1,C^FD<t t-esc="doc.name"/>^FS
                        ^PQ1,0,1,Y
                        ^BY2
                        ^FO70,85^BCN,40,Y,Y,N^FDID:<t t-esc="doc.id"/>^FS
                        ^FB550,15,5,
                        ^XZ
                    """
        else:
            temp = """
                        ^XA
                        
                        ^XZ
                    """
        letters = string.ascii_lowercase
        template_id = ''.join(random.choice(letters) for i in range(50))
        temp_name = "studio_customization." + template_id
        arch_template = """
                            <t t-name=""" + '"' + temp_name + '"' + """>
                                <t t-foreach="docs" t-as="doc">\n""" + temp + """\n
                                </t>
                            </t>
                        """
        report_action_vals = {
            'name': res['name'],
            'report_type': "qweb-text",
            'model': res['selected_model_id'].model,
            'report_name': temp_name,
        }
        report_action_rec = self.env['ir.actions.report'].create(report_action_vals)
        res['report_action_id'] = report_action_rec.id
        report_view_vals = {
            'name': temp_name,
            'type': 'qweb',
            'priority': '16',
            'active': True,
            'mode': 'primary',
            'arch_base': arch_template,
        }
        report_view_rec = self.env['ir.ui.view'].create(report_view_vals)
        res['report_template_id'] = report_view_rec.id
        res['template_id'] = report_view_rec.id
        report_model_data_vals = {
            'module': "studio_customization",
            'name': template_id,
            'display_name': temp_name,
            'model': 'ir.ui.view',
            'res_id': report_view_rec.id,
            'reference': report_view_rec.id,
        }
        report_model_data_rec = self.env['ir.model.data'].create(report_model_data_vals)
        if report_model_data_rec:
            res['report_model_data_id'] = report_model_data_rec.id
            template = """
                                               <template id=""" + '"' + template_id + '"' + """>
                                                    <t t-foreach="docs" t-as="doc">\n""" + temp + """\n
                                                    </t>
                                                </template>
                            """
            res['content'] = arch_template
            #########################################################################################################
            hist = "Template-1"
            data = [(0, 0, {
                'name': hist,
                'template': arch_template,
                'is_selected': True
            })]
            res['zpl_history_ids'] = data
            #########################################################################################################
            if template:
                template = template.replace(""" t-options='{"widget": "float", "precision": 2}'""", "")
            res['content_buffer'] = template
            res['old_content'] = template
        else:
            raise UserError("Sorry! ZPL report could not be created.")

    @api.depends('name', 'content')
    def _compute_zpl_content(self):
        """
        This is a compute method for a computed field 'zpl_content', this method will replace XML code int ZPL code.
        """
        for rec in self:
            if rec.selected_model_id:
                data = self.env[rec.selected_model_id.model].search([], limit=1)
                try:
                    message = rec.content
                    message = message.replace(""" t-options='{"widget": "float", "precision": 2}'""", "")
                    rec.content_buffer = message
                    message = rec.content_buffer
                    index_from = message.rindex('^XA')
                    index_to = message.rindex('^XZ')
                    index_to = index_to + 3
                    message = message[index_from:index_to]
                    while True:
                        try:
                            flag_is_field_exist = message.rindex('t-esc')
                        except:
                            flag_is_field_exist = False
                        if flag_is_field_exist:
                            t_v = message.index('t-esc')
                            rmv_from = t_v - 3
                            on_ward = message[rmv_from:]
                            flag_slash = 0
                            flag_close_tag = 0
                            rmv_to = rmv_from
                            for ch in on_ward:
                                if not flag_slash or flag_close_tag:
                                    if ch == "/":
                                        flag_slash = 1
                                    elif ch == ">":
                                        flag_close_tag = 1
                                    else:
                                        flag_slash = 0
                                    rmv_to = rmv_to + 1
                                else:
                                    rmv_to = rmv_to+1
                                    break
                            t_val = message[rmv_from:rmv_to]
                            field_require = t_val.replace('"/>', '')
                            field_require = field_require.replace('<t t-esc="', '')
                            field_require = field_require[4:]
                            try:
                                field_data = str(data.mapped(field_require)[0])
                            except:
                                raise UserError(
                                    "sorry field : " + field_require + " could not be location in current model")
                                break
                            if field_data:
                                message = message.replace(t_val, field_data)
                        else:
                            break
                    rec.hidden_template = message
                    rec.zpl_content = self.env.ref('sd_zpl_report.zpl_content_template')._render({
                        'message': message,
                    })
                except:
                    rec.zpl_content = ""
            else:
                rec.zpl_content = ""

    @api.onchange('selected_model_id')
    def _onchange_selected_model_id(self):
        """
        if user will want to change the model in which the ZPL Label Report will be available from print menu in form
        view. then this method will be called and after changing the model user also have to click on smart button
        "Add in 'Print' menu".
        """
        for rec in self:
            try:
                rec.report_action_id.model = rec.selected_model_id.model
                rec.report_action_id.unlink_action()
                rec.show_in = False
            except:
                pass

    @api.onchange('name')
    def _onchange_name(self):
        """
        name of the record in this model is actually the name of ZPL Label Report in the selected model's Form view.
        so if user want to change the report name, He/She will simply change the name of the record.
        """
        for rec in self:
            try:
                rec.report_action_id.name = rec.name
            except:
                pass

    @api.onchange('content')
    def _onchange_content(self):
        """
        if you will change in template, then that changes will also be added in actual zpl label report too.
        for that purpose records are updated.
        """
        for rec in self:
            rec.report_template_id.arch_base = rec.content
            content = rec.content
            if content:
                content = content.replace(""" t-options='{"widget": "float", "precision": 2}'""", "")
            rec.content_buffer = content
            if rec.content:
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
                    hist = "Template-"+str(int(hist.split("-")[1])+1)
                except Exception as e:
                    hist = "Template-1"
                new_hist = history.create({'name': hist, 'template': rec.content, 'zpl_design_id': rec._origin.id, 'is_selected': True})
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
                        elements_of_ids = elements_of_ids+str(id)+" "
                    rec.undo_redo = elements_of_ids
                else:
                    last_one = history_ids[-1]
                    lsts = ""
                    for hs in history_ids:
                        if last_one != hs:
                            lsts = lsts + str(hs) + " "
                    rec.undo_redo = str(last_one) + " " + lsts + str(new_hist_id)

    @api.onchange('field_id')
    def _onchange_field_id(self):
        """
        this method will display actual field name of selected model to user, so that user can customize
        the label him/her self when needed.
        """
        for rec in self:
            rec.place_holder = rec.field_id.name

    def zpl_create_action(self):
        """
        this model will add the zpl label report inside selected model form view,
        when user click on smart button "Add in the 'Print' menu".
        """
        for rec in self:
            rec.report_action_id.create_action()
            rec.show_in = True

    def zpl_unlink_action(self):
        """
        this model will remove the zpl label report from selected model form view,
        when user click on smart button "Remove from the 'Print' menu".
        """
        for rec in self:
            rec.report_action_id.unlink_action()
            rec.show_in = False

    def action_redo(self):
        """
            this method will redo the changes made by the user in zpl label template.
            this method makes user of a history model 'zpl.design.history' for this REDO the changes.
        """
        for rec in self:
            if rec.undo_redo:
                undo_redo = rec.undo_redo.strip()
                undo_redo = undo_redo.split(" ")
                undo_redo_vals = []
                for undoredo in undo_redo:
                    undo_redo_vals.append(int(undoredo))
                redo_templates = self.env['zpl.design.history'].search([('zpl_design_id', '=', rec.id)])
                for redo_template in redo_templates:
                    redo_template.is_selected = False
                rotate = 1
                if rec.is_undo:
                    rotate = 2
                for i in range(rotate):
                    required_history_id = undo_redo_vals[-1]
                    last_element = undo_redo_vals[-1]
                    undo_redo_vals.insert(0, last_element)
                    undo_redo_vals.pop(-1)
                redo_template = redo_templates.search([('id', '=', required_history_id)], limit=1)
                redo_template.is_selected = True
                rec.content = redo_template.template
                rec.report_template_id.arch_base = rec.content
                undo_redo_chars = ""
                for undoredo in undo_redo_vals:
                    undo_redo_chars = undo_redo_chars + str(undoredo) + " "
                rec.undo_redo = undo_redo_chars
                rec.is_redo = True
                rec.is_undo = False

    def action_undo(self):
        """
        this method will undo the changes made by the user in zpl label template.
        this method makes user of a history model 'zpl.design.history' for this UNDO the changes.
        """
        for rec in self:
            if rec.undo_redo:
                undo_redo = rec.undo_redo.strip()
                undo_redo = undo_redo.split(" ")
                undo_redo_vals = []
                for undoredo in undo_redo:
                    undo_redo_vals.append(int(undoredo))
                undo_templates = self.env['zpl.design.history'].search([('zpl_design_id', '=', rec.id)])
                for undo_template in undo_templates:
                    undo_template.is_selected = False
                rotate = 1
                if rec.is_redo:
                    rotate = 2
                for i in range(rotate):
                    required_history_id = undo_redo_vals[0]
                    first_element = undo_redo_vals[0]
                    undo_redo_vals.append(first_element)
                    undo_redo_vals.pop(0)
                undo_template = undo_template.search([('id', '=', required_history_id)], limit=1)
                undo_template.is_selected = True
                rec.content = undo_template.template
                rec.report_template_id.arch_base = rec.content
                undo_redo_chars = ""
                for undoredo in undo_redo_vals:
                    undo_redo_chars = undo_redo_chars + str(undoredo) + " "
                rec.undo_redo = undo_redo_chars
                rec.is_redo = False
                rec.is_undo = True

    def action_preview(self):
        """
        this method is for preview the design after making changes in zpl label report by the user.
        """
        CLEANR = re.compile('<.*?>')
        def cleanhtml(raw_html):
            cleantext = re.sub(CLEANR, '', raw_html)
            return cleantext
        density = self.size_id.density
        width = self.size_id.width
        height = self.size_id.height
        zpl = self.hidden_template
        zpl = zpl.replace("‘", "'")
        zpl = zpl.replace("’", "'")
        zpl = zpl.replace("“", "'")
        zpl = zpl.replace("”", "'")
        zpl = cleanhtml(zpl)
        # adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
        url = 'http://api.labelary.com/v1/printers/'+density+'dpmm/labels/'+width+'x'+height+'/0/'
        files = {'file': zpl}
        headers = {}
        failed_flag = 0
        try:
            response = requests.post(url, headers=headers, files=files, stream=True)
            if response.status_code == 200:
                img = base64.b64encode(response.content)
                self.image = img
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'zpl.design.preview',
                    'name': 'ZPL Label Preview',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_image': self.image, 'default_density_choosen': int(density)}
                }
            else:
                failed_flag = 1
        except:
            failed_flag = 1
        if failed_flag:
            raise UserError("Make Sure You Have Internet Connection, ZPL Content To Preview And Provided Correct Width Height and Density in Size Model.")
