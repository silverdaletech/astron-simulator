# -*- coding: utf-8 -*-

import logging

from odoo.http import request
from odoo import _, api, fields, models, tools
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    def _get_needaction_count(self):
        """
        SILVERDALE:: **Override**
        If company based notification is activated, **Override the original
        method to include the company condition in query and then compute
        the number of needaction of the current user, else return super

        """
        company_based_notifications = self.env['ir.config_parameter'].sudo().get_param(
            'sd_company_mail.company_based_notifications')
        if company_based_notifications == 'True':
            self.env['mail.notification'].flush(['is_read', 'res_partner_id'])
            try:
                # self.env.company is not working here, its returning always the same value,
                # so, try to get the current active company id from cookies.
                active_company_id = int(
                    request.httprequest.cookies.get("cids", "").split(",")[0]
                )
            except Exception:
                _logger.info("**********Could not get company from cookies returning company from self.env **********")
                active_company_id = self.env.company.id
            company_id = active_company_id
            self.ensure_one()
            self.env['mail.notification'].flush(['is_read', 'res_partner_id'])
            self.env.cr.execute("""
                        SELECT count(*) as needaction_count
                        FROM mail_notification R
                        WHERE R.res_partner_id = %s AND (R.is_read = false OR R.is_read IS NULL) AND R.company_id = %s""", (self.id, company_id))
            return self.env.cr.dictfetchall()[0].get('needaction_count')
        else:
            return super(Partner, self)._get_needaction_count()
