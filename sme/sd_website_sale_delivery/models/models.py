# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

class sd_delivery(models.Model):
    _inherit = 'delivery.carrier'

    partner_domain = fields.Char(string='Contact Domain')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_delivery_methods(self):
        """
        This function override functionality of shipping method availability on website
        shipping method is only be available for partners that meet domain (partner domain) of shipping method form
        """
        address = self.partner_shipping_id
        carrier = self.env['delivery.carrier'].sudo().search([('website_published', '=', True)]).available_carriers(
            address)
        carrier_parnter_id = []
        for rec in carrier:
            domain = safe_eval(rec.partner_domain) if rec.partner_domain else []
            if domain:
                partner_ids = self.env['res.partner'].search(domain)
                if address in partner_ids:
                    carrier_parnter_id.append(rec.id)
            else:
                carrier_parnter_id.append(rec.id)
        # searching on website_published will also search for available website (_search method on computed field)
        return carrier.filtered(lambda x: x.id in carrier_parnter_id)
