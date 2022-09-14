# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, values):
        res = super(CrmLead, self).create(values)

        template = self.env.ref('sd_crm.mail_template_new_crm_lead')
        activity_type_default_id = self.env['ir.config_parameter'].sudo().get_param('sd_crm.crm_default_activity', 0)
        activity_type_default = self.env['mail.activity.type'].sudo().search([('id', '=', int(activity_type_default_id))])
        if template:
            template.send_mail(res.id, force_send=True)

        if activity_type_default:
            values_list = {
                'summary': activity_type_default.name if activity_type_default.name else 'Review Lead',
                'date_deadline': datetime.now(),
                'user_id': res.user_id.id,
                'res_id': res.id,
                'res_model_id': self.env['ir.model']._get_id('crm.lead'),
                'activity_type_id': activity_type_default.id
            }

            self.env['mail.activity'].sudo().create(values_list)

        return res
