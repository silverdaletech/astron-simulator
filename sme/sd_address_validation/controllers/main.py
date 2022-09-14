# -*- coding: utf-8 -*-

import json
from pyusps import address_information
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class SDWebsiteSale(WebsiteSale):

    @http.route(['/shop/address/selector'], type='http', methods=['GET', 'POST'], auth="public", website=True,
                sitemap=False)
    def address_selector(self, **kw):
        """
        Route for Address selector, if api is called whatever the response is, will be
        displayed in the modal form, If country is not USA then it return to standard method.
        """
        usa_country = request.env['res.country'].sudo().search([('name', '=', 'United States')], limit=1).id
        if kw.get('country_id', False) and kw.get('country_id', False) != str(usa_country):
            return WebsiteSale.address(self, **kw)
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))
        if partner_id == 0:
            partner_id = -1

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ('new', 'shipping')
                        partner_id = -1
                    elif partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')

        # IF POSTED
        if 'submitted' in kw and request.httprequest.method == "POST":
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
            values = kw

        kw_copy = {}
        kw_usps = {}
        if not errors:
            kw_copy = kw.copy()
            kw_usps = kw.copy()

            country_name = ''
            if kw_copy.get('country_id', False):
                country = request.env['res.country'].sudo().search([('id', '=', int(kw_copy.get('country_id')))])
                if country:
                    country_name = country.name
            kw_copy.update({'country_name': country_name})

            state_name = ''
            if kw_copy.get('state_id', False):
                state = request.env['res.country.state'].sudo().search([('id', '=', int(kw_copy.get('state_id')))])
                if state:
                    state_name = state.name
            kw_copy.update({'state_name': state_name})

            if kw:
                response = self._validate_address(kw)
                kw_usps['response_message'] = response.get('response_message')
                kw_usps['error'] = response.get('error', '')
                kw_usps['street'] = response.get('address', '')
                kw_usps['city'] = response.get('city', '')
                kw_usps['state_name'] = response.get('state', '')
                kw_usps['zip'] = response.get('zip5', '') if response.get('zip5', '') else response.get('zip4', '')
                kw_usps['country_name'] = kw_copy.get('country_name')
        submitted = 0
        if kw.get('submitted', False):
            submitted = int(kw.get('submitted'))

        validated = False
        if kw_usps and 'error' in kw_usps:
            validated = True

        render_values = {
            'website_sale_order': order,
            'partner_id': False,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'submitted': submitted,
            'validated': validated,
            'only_services': order and order.only_services,
            'kw': kw_copy,
            'kw_usps': kw_usps,
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)

    @http.route()
    def address(self, **kw):
        """
        Check if kw or kw_usps from the address validation popup are in **kw, if found update the **kw
        """
        if 'kw' in kw:
            kw = json.loads(kw.get('kw'))
        elif 'kw_usps' in kw:
            kw = json.loads(kw.get('kw_usps'))
            country_id = request.env['res.country']
            state_id = request.env['res.country.state']
            if kw.get('country_name'):
                country_id = request.env['res.country'].sudo().search([('name', '=', kw.get('country_name'))])
            if kw.get('state_name') and country_id:
                state = request.env['res.country.state'].sudo().search([('code', '=', kw.get('state_name'))])
                state_id = state.filtered(lambda s: s.country_id == country_id)
            if country_id:
                kw['country_id'] = country_id.id
            if state_id:
                kw['state_id'] = state_id.id
        return super(SDWebsiteSale, self).address(**kw)

    def _validate_address(self, kw):
        """
        Validate address from usps using address_information method
        """
        user_id = request.env['ir.config_parameter'].sudo().get_param('sd_address_validation.usps_user_id') or False
        zip5 = kw.get('zip')
        state_code = ''
        if kw.get('state_id', False):
            state = request.env['res.country.state'].sudo().search([('id', '=', kw.get('state_id'))])
            if state:
                state_code = state.code
        address = {
            'address': kw.get('street') or '',
            'address_extended': kw.get('street2') or '',
            'city': kw.get('city') or '',
            'state': state_code,
            'zip5': zip5
        }
        response = {}
        error = ''
        response_message = ''
        try:
            response = address_information.verify(user_id, address)
        except Exception as e:
            response_message = e
            error = 'Address Not Found.'
        response['response_message'] = str(response_message)
        response['error'] = str(error)
        return response
