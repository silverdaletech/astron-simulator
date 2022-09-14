from odoo.addons.web.controllers import main
from odoo.http import request
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http
from getmac import get_mac_address as gma


class Home(main.Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        """
            Will check IP and mac features enable from setting:
                If IP and mac both enabled and mac and IPs added in user form then it will check both.
                If both match then user can login.
                If only one option is available in setting then it will check only enabled option.
                If any option is  enabled and IPs or Mac not added (Ids length is zero) in user form then It will allow to login
            """
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            mac_address = gma()
            if request.params['login']:
                user_rec = request.env['res.users'].sudo().search(
                    [('login', '=', request.params['login'])])
                ip_enabled = False
                mac_enabled = False
                if user_rec.allowed_ip_ids and request.env['ir.config_parameter'].sudo().get_param(
                        'sd_access_restriction.is_ip_restrict'):
                    ip_enabled = True
                if user_rec.mac_address_ids and request.env['ir.config_parameter'].sudo().get_param(
                        'sd_access_restriction.is_mac_restrict'):
                    mac_enabled = True

                ips = user_rec.allowed_ip_ids.mapped('ip_address')
                macs = user_rec.mac_address_ids.mapped('mac_address')
                if ip_enabled and mac_enabled:
                    if ip_address in ips and mac_address in macs:
                        try:
                            uid = request.session.authenticate(
                                request.session.db,
                                request.params[
                                    'login'],
                                request.params[
                                    'password'])
                            request.params['login_success'] = True
                            return request.redirect(
                                self._login_redirect(uid, redirect=redirect))
                        except odoo.exceptions.AccessDenied as e:
                            request.uid = old_uid
                            if e.args == odoo.exceptions.AccessDenied().args:
                                values['error'] = _("Wrong login/password")
                    else:
                        request.uid = old_uid
                        values['error'] = _("IP or MAC is not valid.")

                elif ip_enabled and not mac_enabled:
                    if ip_address in ips:
                        try:
                            uid = request.session.authenticate(
                                request.session.db,
                                request.params[
                                    'login'],
                                request.params[
                                    'password'])
                            request.params['login_success'] = True
                            return request.redirect(
                                self._login_redirect(uid, redirect=redirect))
                        except odoo.exceptions.AccessDenied as e:
                            request.uid = old_uid
                            if e.args == odoo.exceptions.AccessDenied().args:
                                values['error'] = _("Wrong login/password")
                    else:
                        request.uid = old_uid
                        values['error'] = _("IP  is not valid.")
                elif not ip_enabled and mac_enabled:
                    if mac_address in macs:
                        try:
                            uid = request.session.authenticate(
                                request.session.db,
                                request.params[
                                    'login'],
                                request.params[
                                    'password'])
                            request.params['login_success'] = True
                            return request.redirect(
                                self._login_redirect(uid, redirect=redirect))
                        except odoo.exceptions.AccessDenied as e:
                            request.uid = old_uid
                            if e.args == odoo.exceptions.AccessDenied().args:
                                values['error'] = _("Wrong login/password")
                    else:
                        request.uid = old_uid
                        values['error'] = _("MAC is not valid.")
                else:
                    try:
                        uid = request.session.authenticate(request.session.db,
                                                           request.params[
                                                               'login'],
                                                           request.params[
                                                               'password'])
                        request.params['login_success'] = True
                        return request.redirect(
                            self._login_redirect(uid, redirect=redirect))
                    except odoo.exceptions.AccessDenied as e:
                        request.uid = old_uid
                        if e.args == odoo.exceptions.AccessDenied().args:
                            values['error'] = _("Wrong login/password")

        return request.render('web.login', values)
