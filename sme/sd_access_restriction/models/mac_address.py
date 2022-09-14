from odoo import models, fields
from odoo.http import request


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    mac_address_ids = fields.One2many('allowed.mac', 'user_id', string='Mac')
    is_mac_restriction = fields.Boolean(
        string='Is_ip_restriction_enable', compute='compute_is_mac_restriction',
        required=False)

    def compute_is_mac_restriction(self):
        """
                This function is just to hide and show Mac Address table in user
         """
        self.is_mac_restriction = False
        if request.env['ir.config_parameter'].sudo().get_param('sd_access_restriction.is_mac_restrict'):
            self.is_mac_restriction = True
        else:
            self.is_mac_restriction = False


class AllowedIPs(models.Model):
    _name = 'allowed.mac'

    user_id = fields.Many2one('res.users', string='IP')
    mac_address = fields.Char(string='Mac Address')
