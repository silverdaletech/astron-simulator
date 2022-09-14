# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request


class ConfirmPopUp(models.TransientModel):
    _name = 'confirm.wizard'
    _description = 'Confirm PopUp'

    name = fields.Char()
    user_id = fields.Many2one('res.users', string='User_id')
    login_detail_id = fields.Many2one('user.sessions', string='Login Detail')

    def session_close(self):
        self.login_detail_id.session_close()
        # request.env.user.session.logout(keep_db=True)


# class TimeoutPopUp(models.TransientModel):
#     _name = 'timeout.wizard'
#     _description = 'Session Timeout'
#
#     name = fields.Char()
#     user_id = fields.Many2one('res.users', string='User_id')
#
#     def session_timeout(self):
#         print('function called')

