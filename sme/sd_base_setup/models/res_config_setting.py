from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sd_multi_uninstall = fields.Boolean(
        string='Uninstall multiple Modules')

    sd_license_key = fields.Char(
        string='Silverdale License', config_parameter='sd_base_setup.sd_license_key')

    sd_license_expire = fields.Char(
        string='Silverdale License Expire', config_parameter='sd_base_setup.sd_license_expire')

    is_license_valid = fields.Boolean(string="License Validity", help="Shows if your current license is valid or not.",
                                      config_parameter='sd_base_setup.is_license_valid', readonly=True)
    # Main Extensions
    module_sd_sale = fields.Boolean(
        string='Silverdale Sales Extension')
    module_sd_mail = fields.Boolean(
        string='Silverdale Mail Extension')
    module_sd_account = fields.Boolean(
        string='Silverdale Account Extension')
    module_sd_mrp = fields.Boolean(
        string='Silverdale MRP Extension')
    module_sd_point_of_sale = fields.Boolean(
        string='Silverdale Point of Sales Extension')
    module_sd_contact = fields.Boolean(
        string='Silverdale Contacts Extension')
    module_sd_project = fields.Boolean(
        string='Silverdale Project Extension')
    module_sd_purchase = fields.Boolean(
        string='Silverdale Purchase Extension')
    module_sd_account_check_printing = fields.Boolean(
        string='Silverdale Check Printing Base')
    module_sd_address_validation = fields.Boolean(
        string='USPS Address Validation')
    module_sd_bcc_mail = fields.Boolean(
        string='BCC Emails')
    module_sd_company_mail = fields.Boolean(
        string='Company Based Notifications')
    module_sd_event = fields.Boolean(
        string='Event Extension')
    module_sd_website_slides = fields.Boolean(
        string='eLearning Extension')
    module_sd_helpdesk = fields.Boolean(
        string='Helpdesk Extension')
    module_sd_hr_attendance = fields.Boolean(
        string='Attendance Extension')
    module_sd_document = fields.Boolean(
        string="Silverdale Document Extension")
    module_sd_stock = fields.Boolean(
        string='Silverdale Inventory Extension')
    module_sd_sale_agreement = fields.Boolean(string='Sale Agreements')

    # Generic
    module_sd_maintenace_mode = fields.Boolean(
        string='Website Maintenance Mode')
    module_sd_odoo_audit_data = fields.Boolean(
        string='Audit Master And Duplicate Data')
    module_sd_password_security = fields.Boolean(
        string='Password Security')
    module_sd_public_redirect = fields.Boolean(
        string='URL landing page management')
    module_sd_restrict_multicompany_checkboxes = fields.Boolean(
        string='Restrict Multi-Company Checkboxes')
    module_sd_user_logs = fields.Boolean(
        string='User Log Details')
    module_sd_website_search = fields.Boolean(
        string='SD Website Search')
    module_sd_zpl_report = fields.Boolean(
        string='ZPL Label Designer')
    module_silverdale_odoo_audit = fields.Boolean(
        string='Odoo Audit')
    module_sd_product_brand = fields.Boolean(
        string='Product Brand Manager')
    module_sd_product_defaults = fields.Boolean(
        string='Product Defaults')
    module_sd_user_security_rules = fields.Boolean(
        string='User Security Roles')


    def update_silverdale_license_key(self):
        """
        Check the license validity and set the license validity field based on the response.
        """
        key_respone = self.env['ir.module.module'].get_license_response()
        result = key_respone.get('result', False)
        _logger.info("------------------------------------Result>>>>>>>>>>>>>>>>>>>>>>>>>>>>: " + str(result))

        Config = self.env['ir.config_parameter'].sudo()
        if  result and result.get('status', False) == True:
            message = "Your licence key is valid."
            Config.set_param('sd_base_setup.is_license_valid', True)
        else:
            Config.set_param('sd_base_setup.is_license_valid', False)
            message = "Your licence key is not valid. You can check your subscription here at " \
                      "silverdaletech.com/my/subscription. "
            # self.env['ir.module.module'].update_silverdale_module()

        view_id = self.env.ref(
            'sd_base_setup.sd_message_wizard_form').id
        value = {
            'name': _('License Validity Status'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sd.message.wizard',
            'view_id': False,
            'context': {'message': message},
            'views': [(view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return value
