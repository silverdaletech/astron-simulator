from odoo import models, fields
from odoo.http import request


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    allowed_ip_ids = fields.One2many('allowed.ips', 'user_id', string='IP')
    is_ip_restriction = fields.Boolean(
        string='Is_ip_restriction_enable', compute='compute_is_ip_restriction',
        required=False)

    def compute_is_ip_restriction(self):
        """
        This function is just to hide and show IPs table in user
        """
        self.is_ip_restriction = False
        if request.env['ir.config_parameter'].sudo().get_param('sd_access_restriction.is_ip_restrict'):
            self.is_ip_restriction = True
        else:
            self.is_ip_restriction = False


class AllowedIPs(models.Model):
    _name = 'allowed.ips'

    user_id = fields.Many2one('res.users', string='IP')
    ip_address = fields.Char(string='Allowed IP')
