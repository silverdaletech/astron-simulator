# -*- coding: utf-8 -*-

import pdb

from odoo import fields, models, api


class MailNotification(models.Model):
    """
    Introduce company in notifications, company is populated when notification
    is created in mail.thread [_notify_record_by_inbox method]
    """
    _inherit = 'mail.notification'

    company_id = fields.Many2one('res.company', 'Company')
