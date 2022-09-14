from odoo import models, fields, api, _


class AddressSelector(models.TransientModel):
    _name = 'usps.address.selector'
    _description = 'Address Selector'

    current_street = fields.Char(string="Street")
    current_street_2 = fields.Char(string="Street 2")
    current_city = fields.Char(string="City")
    current_zip = fields.Char(string="ZIP")
    current_state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Current State',
        required=False)
    current_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Current Country',
        required=False)

    updated_street = fields.Char(string="Street")
    updated_street_2 = fields.Char(string="Street 2")
    updated_city = fields.Char(string="City")
    updated_zip = fields.Char(string="ZIP")
    updated_state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Current State',
        required=False)
    updated_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        required=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='partner',
        required=False)

    def button_validated_address(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.sudo().write({
                    'street': rec.updated_street or '',
                    'street2': rec.updated_street_2 or '',
                    'city': rec.updated_city or '',
                    'state_id': rec.updated_state_id or False,
                    'zip': rec.updated_zip or '',
                    'date_validated': fields.Datetime.now(),
                    'validation_failed': False,
                    'validation_status': 'valid',
                    'validation_message': "Contact is valid and validated on %s" % fields.Datetime.now(),
                })

    def button_keep_address(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.sudo().write({
                    'date_validated': fields.Datetime.now(),
                    'validation_failed': False,
                    'validation_status': 'valid',
                    'validation_message': "Contact is valid and validated on %s" % fields.Datetime.now()
                })
