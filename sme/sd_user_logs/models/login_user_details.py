# -*- coding: utf-8 -*-
import time
from datetime import date, datetime, timedelta

from itertools import chain
from odoo.http import request
from odoo import http, models, fields, api
import logging, socket
# from getmac import get_mac_address
_logger = logging.getLogger(__name__)
USER_PRIVATE_FIELDS = ['password']
concat = chain.from_iterable
from odoo.http import OpenERPSession


def logout_inherit(self, keep_db=False):
    try:
        current = datetime.now()
        userid = self.uid
        # mac = get_mac_address()
        user = request.env['res.users'].search([('id', '=', userid)])

        records = request.env['user.sessions'].search([('user_id', '=', userid), ('session_status', '=', 'active')])
        for rec in records:
            rec.write({'end_date_time': current,
                       'session_status': 'inactive'
                       })
        if user.is_active_session:
            is_user = user.sudo().write({'is_active_session': False})
    except Exception as ex:
        print("logout_inherit method error : ", ex)

    for k in list(self):
        if not (keep_db and k == 'db') and k != 'debug':
            del self[k]
    self._default_values()
    self.rotate = True

OpenERPSession.logout = logout_inherit

OpenERPSession.logout = logout_inherit


class IrHTTP(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, endpoint):
        res = super(IrHTTP, cls)._authenticate(endpoint=endpoint)
        auth_method = endpoint.routing["auth"]
        if auth_method == "user" and request and request.env and request.env.user and request.env.user.company_id.enforce_time_interval:
            request.env.user.auth_timeout_check()
        return res

    @classmethod
    def _auth_method_user(cls):
        request.uid = request.session.uid
        user = request.env['res.users'].search([('id', '=', request.uid)])
        if not request.uid:
            raise http.SessionExpiredException("Session expired")
        if user.is_active_session:
            user.sudo().is_active_session = False
            request.session.logout(keep_db=True)
            raise http.SessionExpiredException("Session expired")


class LoginUpdate(models.Model):
    _name = 'user.sessions'
    _description = 'User Session Details'
    _rec_name = "user_id"

    user_id = fields.Many2one('res.users', string="User Name")
    start_date_time = fields.Datetime(string="Login Date And Time", default=lambda self: fields.datetime.now())
    end_date_time = fields.Datetime(string="Logout Date And Time", default=lambda self: fields.datetime.now())
    ip_address = fields.Char(string="IP Address")
    socket_name = fields.Char(string="Host Name")
    # mac_address = fields.Char(string="Mac Address")
    browser = fields.Char(string="Browser")
    session_status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Session Status')

    def action_confirm_wizard(self):
        self.ensure_one()
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "confirm.wizard",
            # "res_id": self.id,
            "name": "Confirm Session End",
            "views": [[False, "form"]],
            "context": {"create": False,
                        "default_user_id": self.user_id.id,
                        "default_login_detail_id": self.id,
                        },
            "target": "new",

        }
        return action_window

    def session_close(self):
        existing_recs = self.search([('user_id', '=', self.user_id.id), ('session_status', '=', 'active')])
        for rec in existing_recs:
            rec.user_id.is_active_session = True
            rec.end_date_time = datetime.now()
            rec.session_status = 'inactive'
            self.env.cr.commit()
