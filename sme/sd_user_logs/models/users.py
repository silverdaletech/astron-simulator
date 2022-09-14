# -*- coding: utf-8 -*-
import time
from datetime import date, datetime, timedelta

from itertools import chain
from os import utime
import logging, socket

from dateutil.relativedelta import relativedelta
from odoo.http import request
from odoo import http, models, fields, api
from odoo.http import SessionExpiredException

_logger = logging.getLogger(__name__)

# from getmac import get_mac_address


class LoginUserDetail(models.Model):
    _inherit = 'res.users'
    is_active_session = fields.Boolean(
        string='Is Active Session',
        default=False)

    user_sessions_ids = fields.One2many('user.sessions', inverse_name='user_id', string='User Sessions')

    def _auth_timeout_deadline_calculate(self):
        interval_type = self.env.user.company_id.interval_type
        interval_number = self.env.user.company_id.interval_number
        today = datetime.today()
        result = False
        if interval_type == 'hours' and self.login_date:
            td = timedelta(hours=interval_number)
            result = self.login_date + td

        if interval_type == 'days' and self.login_date:
            td = timedelta(days=interval_number)
            result = self.login_date + td

        if interval_type == 'weeks' and self.login_date:
            td = timedelta(weeks=interval_number)
            result = self.login_date + td

        if interval_type == 'months' and self.login_date:
            result = self.login_date + relativedelta(months=interval_number)

        return result

    @api.model
    def _auth_timeout_session_terminate(self, session):
        """Pluggable method for terminating a timed-out session

        This is a late stage where a session timeout can be aborted.
        Useful if you want to do some heavy checking, as it won't be
        called unless the session inactivity deadline has been reached.

        Return:
            True: session terminated
            False: session timeout cancelled
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    @api.model
    def auth_timeout_check(self):
        """Perform session timeout validation and expire if needed."""

        if not http.request:
            return

        session = http.request.session

        # Calculate deadline
        deadline = self._auth_timeout_deadline_calculate()
        today = datetime.today()

        # Check if past deadline
        expired = False
        if deadline and deadline < today:

            # self.sudo().action_timeout_wizard()
            sessions = self.user_sessions_ids.sudo().session_close()
            expired = True

        # Try to terminate the session
        terminated = False
        if expired:
            terminated = self._auth_timeout_session_terminate(session)

        # If session terminated, all done
        if terminated:
            raise SessionExpiredException("Session expired")

    @api.model
    def _check_credentials(self, password, user_agent_env):
        """
        This function will create record in login detail model when user login to system
        containing values username,and IP address.
        """
        result = super(LoginUserDetail, self)._check_credentials(password, user_agent_env)
        try:
            self.sudo().is_active_session = False
            vals = {'user_id': self.id,
                    'ip_address': request.httprequest.environ['REMOTE_ADDR'],
                    'socket_name': socket.gethostname(),
                    # 'mac_address': get_mac_address(),
                    'browser': request.httprequest.user_agent.browser,
                    'session_status': 'active',
                    }
            self.env['user.sessions'].sudo().create(vals)
        except Exception as ex:
            print("_check_credentials method error : ", ex)
        return result

    # def action_timeout_wizard(self):
    #     values = {
    #         'default_user_id': self.id,
    #     }
    #     return request.env['ir.ui.view'].sudo()._render_template('sd_user_logs.user_timeout_popup')
