# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SlideChannelMailwizard(models.TransientModel):
    _name = "slide.channel.mail.wizard"
    course_ids = fields.Many2many('slide.channel')
    partner_ids = fields.Many2many('res.partner')
    email_template_id = fields.Many2one('mail.template')

    @api.model
    def default_get(self, fields):
        vals = super(SlideChannelMailwizard, self).default_get(fields)
        # course_ids = self.env['account.move'].browse(active_ids)
        course_ids = self._context.get('active_ids')
        course_ids = self.env['slide.channel'].browse(course_ids)
        email_template_id = self.env.ref('sd_invite_multiple_attendees.mail_template_invite_multiple_attendees', raise_if_not_found=False)
        vals['course_ids'] = course_ids
        vals['email_template_id'] = email_template_id
        return vals
    
    def action_apply(self):
        emails = set(r['email'] for r in self.partner_ids if r.email)
        email_values = {
            'email_to': ','.join(emails)
        }

        print(email_values)
        for course in self.course_ids:
            self.email_template_id.send_mail(course.id, force_send=True, email_values=email_values)
            for user in self.partner_ids.filtered(lambda self:self.email != False):
                if user.email:
                    course._action_add_members(user)
