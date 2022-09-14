# -*- coding: utf-8 -*-

import re
from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID, Command
from odoo import _, api, fields, models, tools


# main mako-like expression pattern
EXPRESSION_PATTERN = re.compile('(\$\{.+?\})')


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

    email_bcc = fields.Char('Email BCC')

    def get_mail_values(self, res_ids):
        """This function will  get email bcc from mail wizard"""
        res = super(MailComposer, self).get_mail_values(res_ids)
        if self.is_log:
            return res

        for r in res.keys():
            rec = self.filtered(lambda x: x.res_id == r)
            if rec:
                res[r].update({
                               'email_bcc': rec.email_bcc or '',
                               })
                mass_mail_mode = self.composition_mode == 'mass_mail'
        return res

    def _onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        if template_id and composition_mode == 'mass_mail':
            template = self.env['mail.template'].browse(template_id)
            fields = ['subject', 'body_html', 'email_from', 'reply_to', 'mail_server_id']
            values = dict((field, getattr(template, field)) for field in fields if getattr(template, field))
            if template.attachment_ids:
                values['attachment_ids'] = [att.id for att in template.attachment_ids]
            if template.mail_server_id:
                values['mail_server_id'] = template.mail_server_id.id
            if template.email_bcc:
                values['email_bcc'] = template.email_bcc
        elif template_id:
            values = self.generate_email_for_composer(
                template_id, [res_id],
                ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'email_bcc', 'reply_to', 'attachment_ids', 'mail_server_id']
            )[res_id]
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if email not send
            attachment_ids = []
            Attachment = self.env['ir.attachment']
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                attachment_ids.append(Attachment.create(data_attach).id)
            if values.get('attachment_ids', []) or attachment_ids:
                values['attachment_ids'] = [Command.set(values.get('attachment_ids', []) + attachment_ids)]
        else:
            default_values = self.with_context(default_composition_mode=composition_mode, default_model=model, default_res_id=res_id).default_get(['composition_mode', 'model', 'res_id', 'parent_id', 'partner_ids', 'subject', 'body', 'email_from', 'reply_to', 'attachment_ids', 'mail_server_id'])
            values = dict((key, default_values[key]) for key in ['subject', 'body', 'partner_ids', 'email_from', 'reply_to', 'attachment_ids', 'mail_server_id'] if key in default_values)

        if values.get('body_html'):
            values['body'] = values.pop('body_html')
        if values.get('email_bcc'):
            values['email_bcc'] = values.pop('email_bcc')

        # This onchange should return command instead of ids for x2many field.
        values = self._convert_to_write(values)

        return {'value': values}

