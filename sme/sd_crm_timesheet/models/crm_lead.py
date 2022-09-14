# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CRMLead(models.Model):
    _name = 'crm.lead'
    _inherit = ["crm.lead", "timer.mixin"]

    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='lead_id',
        string='Timesheets',
        required=False)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    display_timesheet_timer = fields.Boolean("Display Timesheet Time", compute='_compute_display_timesheet_timer')
    display_timer_start_secondary = fields.Boolean(compute='_compute_display_timer_buttons')

    effective_hours = fields.Float("Hours Spent", compute='_compute_effective_hours', compute_sudo=True, store=True,
                                   help="Time spent on this lead")
    total_hours_spent = fields.Float("Total Hours", compute='_compute_total_hours_spent', store=True,
                                     help="Time spent on this lead")
    encode_uom_in_days = fields.Boolean(compute='_compute_encode_uom_in_days', default=lambda self: self._uom_in_days())

    def _compute_encode_uom_in_days(self):
        self.encode_uom_in_days = self._uom_in_days()

    def _uom_in_days(self):
        return self.env.company.timesheet_encode_uom_id == self.env.ref('uom.product_uom_day')

    @api.depends('effective_hours')
    def _compute_total_hours_spent(self):
        for lead in self:
            lead.total_hours_spent = lead.effective_hours

    @api.depends('timesheet_ids.unit_amount')
    def _compute_effective_hours(self):
        for lead in self:
            lead.effective_hours = round(sum(lead.timesheet_ids.mapped('unit_amount')), 2)

    def action_create_analytic_account(self):
        for rec in self:
            account = self.env['account.analytic.account'].create({
                'name': rec.name,
                'partner_id': rec.partner_id.id or False,
            })
            rec.account_analytic_id = account.id

    @api.depends('account_analytic_id')
    def _compute_display_timesheet_timer(self):
        for lead in self:
            display_timesheet_timer = False
            if lead.account_analytic_id:
                display_timesheet_timer = True
            lead.display_timesheet_timer = display_timesheet_timer

    @api.depends('display_timesheet_timer', 'timer_start', 'timer_pause', 'total_hours_spent')
    def _compute_display_timer_buttons(self):
        for lead in self:
            if not lead.display_timesheet_timer:
                lead.update({
                    'display_timer_start_primary': False,
                    'display_timer_start_secondary': False,
                    'display_timer_stop': False,
                    'display_timer_pause': False,
                    'display_timer_resume': False,
                })
            else:
                super(CRMLead, lead)._compute_display_timer_buttons()
                lead.display_timer_start_secondary = lead.display_timer_start_primary
                if not lead.timer_start:
                    lead.update({
                        'display_timer_stop': False,
                        'display_timer_pause': False,
                        'display_timer_resume': False,
                    })
                    if not lead.total_hours_spent:
                        lead.display_timer_start_secondary = False
                    else:
                        lead.display_timer_start_primary = False

    def action_timer_start(self):
        if not self.user_timer_id.timer_start and self.display_timesheet_timer:
            super(CRMLead, self).action_timer_start()

    def action_timer_stop(self):
        # timer was either running or paused
        if self.user_timer_id.timer_start and self.display_timesheet_timer:
            rounded_hours = self._get_rounded_hours(self.user_timer_id._get_minutes_spent())
            return self._action_open_new_timesheet(rounded_hours)
        return False

    def _get_rounded_hours(self, minutes):
        minimum_duration = int(self.env['ir.config_parameter'].sudo().get_param('sd_crm_timesheet.sd_timesheet_min_duration',0))
        rounding = int(self.env['ir.config_parameter'].sudo().get_param('sd_crm_timesheet.sD_timesheet_rounding', 0))
        rounded_minutes = self._timer_rounding(minutes, minimum_duration, rounding)
        return rounded_minutes / 60

    def _action_open_new_timesheet(self, time_spent):
        return {
            "name": _("Confirm Time Spent"),
            "type": 'ir.actions.act_window',
            "res_model": 'crm.lead.create.timesheet',
            "views": [[False, "form"]],
            "target": 'new',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': self._name,
                'default_time_spent': time_spent,
            },
        }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(SaleOrder, self).create(vals_list)
        for rec in res_ids:
            if rec.opportunity_id and rec.opportunity_id.account_analytic_id:
                rec.analytic_account_id = rec.opportunity_id.account_analytic_id
        return res_ids
