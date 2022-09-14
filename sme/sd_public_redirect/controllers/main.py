# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home


class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        """
            Session will come from Rander function.
        """
        if not redirect:
            redirect = request.session.get('previous_url', None)

        return super(Home, self).web_login(redirect, **kw)
