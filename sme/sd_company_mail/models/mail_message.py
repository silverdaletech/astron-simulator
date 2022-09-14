# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.http import request


class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _search_needaction(self, operator, operand):
        """
        SILVERDALE:: **Override**
        Include the current company in domain if company based notification is activated else call return super
        """
        company_based_notifications = self.env['ir.config_parameter'].sudo().get_param(
            'sd_company_mail.company_based_notifications')
        if company_based_notifications == 'True':
            is_read = False if operator == '=' and operand else True
            try:
                # self.env.company is not working here, its returning always the same value,
                # so, try to get the current active company id from cookies.
                active_company_id = int(
                    request.httprequest.cookies.get("cids", "").split(",")[0]
                )
            except Exception:
                active_company_id = self.env.company.id

            company_id = active_company_id
            notification_ids = self.env['mail.notification']._search([('res_partner_id', '=', self.env.user.partner_id.id), ('is_read', '=', is_read), ('company_id', '=', company_id)])
            return [('notification_ids', 'in', notification_ids)]
        else:
            return super(Message, self)._search_needaction(operator, operand)

    def get_company(self):
        """
        **Called from JS**
        Returns notification's company_id or False
        """
        company_based_notifications = self.env['ir.config_parameter'].sudo().get_param(
            'sd_company_mail.company_based_notifications')
        company = False
        if company_based_notifications == 'True' and self.notification_ids:
            notif = self.notification_ids[0]
            if notif.company_id:
                company = notif.company_id.id
        return company
