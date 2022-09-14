from odoo import api, fields, models, tools


class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'
    default_user_ids = fields.Many2many("res.users", string="Default Users")


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    user_ids = fields.Many2many(
        'res.users',
        default=lambda self: self.env.user,
        index=True, required=False)

    @api.onchange('user_id')
    def _on_change_user_id(self):
        if not self.activity_type_id.default_user_ids:
            self.user_ids = self.user_id
    
    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        if self.activity_type_id:
            if self.activity_type_id.summary:
                self.summary = self.activity_type_id.summary
            self.date_deadline = self._calculate_date_deadline(self.activity_type_id)
            self.user_id = self.activity_type_id.default_user_id or self.env.user

            if self.activity_type_id.default_user_ids:
                self.user_ids = self.activity_type_id.default_user_ids or self.env.user
                self.user_id = self.activity_type_id.default_user_ids[0].id

            if self.activity_type_id.default_note:
                self.note = self.activity_type_id.default_note

    def action_close_dialog(self):
        res = super(MailActivity, self).action_close_dialog()
        for user in self.user_ids.filtered(lambda user:user.id != self.user_id.id):
            values_list = {
            'res_id': self.res_id,
            'res_model_id': self.res_model_id.id,
            'activity_type_id': self.activity_type_id.id,
            'user_id': user.id,
            'user_ids': user,
            'date_deadline': self.date_deadline,
            'summary': self.summary,
            'note': self.note,
            }
            activities = self.env['mail.activity'].create(values_list)
        self.user_ids = self.user_id
        return res
        return {'type': 'ir.actions.act_window_close'}

