# -*- coding: utf-8 -*-

import pdb

from odoo import fields, models, api


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_record_company(self, values=False):
        """
        Return the company related to the document
        """
        company = False
        if 'model' in values and 'res_id' in values:
            model = values.get('model', self.env.context.get('default_model'))
            res_id = values.get('res_id', self.env.context.get('default_res_id'))
            if not model or not res_id or model not in self.env:
                return False
            record_id = self.env[model].sudo().browse(res_id)
            if record_id and 'company_id' in record_id:
                company = record_id.company_id.id
        return company

    def _notify_record_by_inbox(self, message, recipients_data, msg_vals=False, **kwargs):

        """
        SILVERDALE:: **Override**
        Call super and add write company in notification
        """
        res = super(MailThread, self)._notify_record_by_inbox(message, recipients_data, msg_vals=msg_vals, **kwargs)
        if message and msg_vals:
            notification_id = self.env['mail.notification'].sudo().search([('mail_message_id', '=', message.id)])
            company_id = self._get_record_company(msg_vals)
            if notification_id:
                notification_id.company_id = company_id
        return res
