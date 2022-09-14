import datetime

from odoo.http import HttpRequest
from odoo.http import Response
from odoo.http import request


def render(self, template, qcontext=None, lazy=True, **kw):
    """
    This will call maintenance template while upgrade process
    """
    is_installed = self.env['ir.module.module'].sudo().search(
        [('name', '=', 'sd_maintenace_mode'), ('state', '=', 'installed')], limit=1)
    if is_installed:
        admin_user = self.env.company.admin_user.id
        is_upgrade_website = self.env['ir.config_parameter'].sudo().get_param(
            'sd_maintenace_mode.website_maintenance_mode', False)
        if is_upgrade_website == 'True':
            if not request.env.user or not request.env.user.id == admin_user and request.httprequest.path != '/web':
                template = 'sd_maintenace_mode.maintenance'
                end_date = self.env.company.upgrade_end_date or datetime.datetime.now()
                delay = end_date - datetime.datetime.now()
                qcontext['delay'] = delay.total_seconds()

    response = Response(template=template, qcontext=qcontext, **kw)
    if not lazy:
        return response.render()
    return response


# Override python base function
HttpRequest.render = render
