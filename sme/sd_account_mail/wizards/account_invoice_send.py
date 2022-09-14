# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools, Command


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    current_followers_ids = fields.Many2many('mail.followers', 'mail_followers_account_invoices_relation',
                              'mail_followers_id', 'account_invoices_id', string="Followers")
    is_followers_exist = fields.Boolean()
    allowed_users = fields.Many2many('res.partner', 'account_invoice_send_res_partner_rel2', 'wizard_id', 'partner_id', 'Allowed Contacts', compute='compute_allowed_users')
    # from_email_partner_id = fields.Many2one('res.partner', string='From Email', default=lambda self: self.env.user.partner_id)

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceSend, self).default_get(fields)
        try:
            model = self.env.context.get('default_model')
            active_id = self.env.context.get('default_res_id', False)
            rec = self.env[model].search([('id', '=', active_id)])
            if rec.message_follower_ids.ids:
                res['current_followers_ids'] = rec.message_follower_ids.ids
                res['is_followers_exist'] = True
            else:
                res['is_followers_exist'] = False
        except:
            self.is_followers_exist = False
        return res

    @api.onchange('from_email_partner_id')
    def compute_allowed_users(self):
        allowed_users_list = []
        current_partner = self.env.user.partner_id
        if current_partner and current_partner.company_type == 'company':
            allowed_users_list = current_partner.child_ids.ids
        elif current_partner and current_partner.company_type == 'person' and current_partner.parent_id:
            allowed_users_list = current_partner.parent_id.child_ids.ids
        else:
            allowed_users_list.append(current_partner.id)
        self.allowed_users = allowed_users_list
