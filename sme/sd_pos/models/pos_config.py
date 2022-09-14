# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    has_pos_specific_info = fields.Boolean(string="POS specific logo and address")
    logo = fields.Binary(string="POS Logo", readonly=False)
    set_logo = fields.Boolean(string="POS Specific Logo")
    set_address = fields.Boolean(string="POS Specific Address")
    print_closing_stats = fields.Boolean(string="Print POS Closing Stats")
    show_tips_in_closing_stats = fields.Boolean(string="Show Tips in POS Closing Stats")
    show_selectable_lots = fields.Boolean(string="Show Selectable Lots")
    auto_print_closing_stats = fields.Boolean(string="Auto Print Pos Closing Stats")

    phone = fields.Char()
    vat = fields.Char()
    email = fields.Char()
    website = fields.Char()

    @api.onchange('iface_tipproduct')
    def _sd_onchange_iface_tipproduct(self):
        if not self.iface_tipproduct:
            self.show_tips_in_closing_stats = False

    @api.onchange('has_pos_specific_info')
    def _sd_onchange_has_pos_specific_info(self):
        if not self.has_pos_specific_info:
            self.logo = False
            self.set_logo = False
            self.set_address = False
            self.phone = False
            self.vat = False
            self.email = False
            self.website = False

    @api.onchange('set_logo')
    def _sd_onchange_set_logo(self):
        if not self.set_logo:
            self.logo = False

    @api.onchange('set_address')
    def _sd_onchange_set_address(self):
        if not self.set_address:
            self.phone = False
            self.vat = False
            self.email = False
            self.website = False

