from odoo import api, fields, models, tools


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    def action_multiple_email_send(self):
        composer_form_view_id = self.env.ref('mail.email_compose_message_wizard_form').id

        template_id = self._get_email_template().id

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': composer_form_view_id,
            'target': 'new',
            'context': {
                'default_composition_mode': 'mass_mail' if len(self.ids) > 1 else 'comment',
                'default_res_id': self.ids[0],
                'default_model': 'slide.channel',
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'active_ids': self.ids,
            },
        }

    def _get_email_template(self):
        """
        Return the cart recovery template record for a set of orders.
        If they all belong to the same website, we return the website-specific template;
        otherwise we return the default template.
        If the default is not found, the empty ['mail.template'] is returned.
        """
        template = self.env.ref('sd_invite_multiple_attendees.mail_template_invite_multiple_attendees', raise_if_not_found=False)
        return template