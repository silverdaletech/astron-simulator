# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
import base64


class MailComposer(models.TransientModel):
    """ Generic message composition wizard. You may inherit from this wizard
        at model and view levels to provide specific features.

        The behavior of the wizard depends on the composition_mode field:
        - 'comment': post on a record. The wizard is pre-populated via ``get_record_data``
        - 'mass_mail': wizard in mass mailing mode where the mail details can
            contain template placeholders that will be merged with actual data
            before being sent to each recipient.
    """
    _inherit = 'mail.compose.message'

    allowed_users = fields.Many2many('res.partner', 'mail_compose_message_res_partner_rel2', 'wizard_id', 'partner_id', 'Allowed Contacts', compute='compute_allowed_users')

    from_email_partner_id = fields.Many2one('res.partner', string='From Email', default=lambda self: self.env.user.partner_id)
    current_followers_ids = fields.Many2many('mail.followers', 'mail_followers_composer_relation',
                                             'mail_follower_id', 'mail_composer_messages_id', string="Followers")
    is_followers_exist = fields.Boolean()

    @api.model
    def default_get(self, fields):
        try:
            res = super(MailComposer, self).default_get(fields)
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

    def get_mail_values(self, res_ids):
        """Generate the values that will be used by send_mail to create mail_messages
        or mail_mails. """
        self.ensure_one()
        if self.from_email_partner_id.email:
            self.email_from = self.from_email_partner_id.email_formatted

        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == 'mass_mail'

        # render all template-based value at once
        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        # compute alias-based reply-to in batch
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.reply_to_force_new:
            records = self.env[self.model].browse(res_ids)
            reply_to_value = records._notify_get_reply_to(default=self.email_from)

        for res_id in res_ids:
            # static wizard (mail.message) values
            mail_values = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'partner_ids': [partner.id for partner in self.partner_ids],
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'reply_to_force_new': self.reply_to_force_new,
                'mail_server_id': self.mail_server_id.id,
                'mail_activity_type_id': self.mail_activity_type_id.id,
            }

            # mass mailing: rendering override wizard static values
            if mass_mail_mode and self.model:
                record = self.env[self.model].browse(res_id)
                mail_values['headers'] = record._notify_email_headers()
                # keep a copy unless specifically requested, reset record name (avoid browsing records)
                mail_values.update(is_notification=not self.auto_delete_message, model=self.model, res_id=res_id, record_name=False)
                # auto deletion of mail_mail
                if self.auto_delete or self.template_id.auto_delete:
                    mail_values['auto_delete'] = True
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values.update(email_dict)
                if not self.reply_to_force_new:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if self.reply_to_force_new and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [Command.link(id) for id in mail_values.pop('partner_ids', [])]

                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.env['ir.attachment'].browse(attach_id).copy({'res_model': self._name, 'res_id': self.id})
                    attachment_ids.append(new_attach_id.id)
                attachment_ids.reverse()
                mail_values['attachment_ids'] = self.env['mail.thread'].with_context(attached_to=record)._message_post_process_attachments(
                    mail_values.pop('attachments', []),
                    attachment_ids,
                    {'model': 'mail.message', 'res_id': 0}
                )['attachment_ids']

            results[res_id] = mail_values

        results = self._process_state(results)
        return results