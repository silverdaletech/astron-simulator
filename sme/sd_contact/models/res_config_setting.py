# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_address_validation = fields.Boolean(
        string='USPS Address Validation')

    module_sd_partner_firstname = fields.Boolean(
        string='Partner first name and last name')

    module_sd_partner_pricelist = fields.Boolean(
        string='Partners Pricelist')

    module_sd_portal_access_account = fields.Boolean(
        string='Enable of Disable user to access Invoices on Portal')

    module_sd_portal_access_sale = fields.Boolean(
        string='Enable of Disable user to access Sale Order/Quotations on Portal')

    module_sd_portal_access_helpdesk = fields.Boolean(
        string='Enable of Disable user to access Helpdesk Tickets on Portal')

    module_sd_portal_access_project = fields.Boolean(
        string='Enable of Disable user to access Projects on Portal')

    module_sd_portal_access_purchase = fields.Boolean(
        string='Enable of Disable user to access Purchases on Portal')

    module_sd_portal_access_timesheet = fields.Boolean(
        string='Enable of Disable user to access timesheet on Portal')
