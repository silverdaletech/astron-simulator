# -*- coding: utf-8 -*-

from odoo import models, fields, api
from pyusps import address_information
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Partner(models.Model):
    _inherit = 'res.partner'

    date_validated = fields.Datetime('Address validated', readonly=True, index=True)
    validation_failed = fields.Boolean('Validation Failed', readonly=True, index=True, )
    address_updated = fields.Boolean('address updated', readonly=True, index=True, )
    validation_message = fields.Char(
        string='Validation Message',
        required=False)
    validation_status = fields.Selection(
        string='Validation_status',
        selection=[('valid', 'valid'),
                   ('invalid', 'invalid'),
                   ('not-validated', 'Not Validated'),
                   ],
        required=False, default='not-validated')

    def button_validate_addrese_cron(self):
        auto_revalidate = self.env.user.company_id.auto_revalidate
        number_of_period = self.env.user.company_id.number_of_period
        today = datetime.today()
        if auto_revalidate == 'week':
            td = timedelta.Timedelta(weeks=number_of_period)
            result = today - td
        if auto_revalidate == 'months':
            result = datetime.today() + relativedelta(months=-(number_of_period))
        if auto_revalidate == 'years':
            result = datetime.today() + relativedelta(years=-(number_of_period))

        for partner in self.env['res.partner'].search([('address_updated', '>=', result)]):
            partner.with_context(scheduler_run=True).button_validate_address()
            partner['address_updated'] = True

    def button_validate_address(self, raise_error=True):
        user_id = request.env['ir.config_parameter'].sudo().get_param('sd_address_validation.usps_user_id') or False
        for rec in self:
            if not user_id or not rec.country_id or rec.country_id.code != 'US':
                continue

            response = False
            zip5 = rec.zip and rec.zip.strip().split('-')[0] or ''
            addr = {
                'address': rec.street or '',
                'address_extended': rec.street2 or '',
                'city': rec.city or '',
                'state': rec.state_id.code or '',
                'zip5': zip5,
            }

            try:
                response = address_information.verify(user_id, addr)
            except Exception as e:
                rec.validation_failed = True
                rec.validation_status = 'invalid'
                rec.date_validated = fields.Datetime.now()
                if not self.env.context.get('scheduler_run', False):
                    if raise_error:
                        rec.validation_message = "Address is not valid for reason\n" + str(e)
                        # raise ValidationError(str(e) + "for partner " + str(rec.name))

            if response:
                state = self.env['res.country.state'].search([
                    ('code', '=', response['state']),
                    ('country_id', '=', rec.country_id.id),
                ], limit=1)
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Address Selector',
                    'view_mode': 'form',
                    'target': 'new',
                    'res_model': 'usps.address.selector',
                    'context': {'default_current_street': rec.street or '',
                                'default_current_street_2': rec.street2 or '',
                                'default_current_city': rec.city or '',
                                'default_current_zip': rec.zip or '',
                                'default_current_state_id': rec.state_id.id,
                                'default_current_country_id': rec.country_id.id,
                                'default_updated_street': response.get('address', False),
                                'default_updated_street_2': response.get('address_extended', False),
                                'default_updated_city': response.get('city', False),
                                'default_updated_zip': response.get('zip4', False) and response['zip5'] + '-' +
                                                       response['zip4'] or response.get(
                                    'zip5'),
                                'default_updated_state_id': state and state.id or False,
                                'default_partner_id': rec.id,

                                }
                }

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        if request.env['ir.config_parameter'].sudo().get_param('sd_address_validation.address_check_on_creation'):
            res.button_validate_address(raise_error=True)
        return res