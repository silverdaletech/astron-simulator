from odoo import api, models, fields, _ 
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import datetime

class WOProducedQty(models.TransientModel):
    _name = 'wo.produced.qty.wizard'
    _description = 'Workorder Produced Qty'

    workorder_id = fields.Many2one('mrp.workorder')
    qty_production = fields.Float(related="workorder_id.qty_production")
#     assign_qty = fields.Float(related="workorder_id.assign_qty")
    qty = fields.Float()
    produced_range = fields.Char(string="Range")
    badge_number = fields.Char(string="Badge/ID")
    date_start = fields.Datetime(string="Start Date")
    date_end = fields.Datetime(string="End Date")
    employee_id = fields.Many2one('hr.employee', readonly=True)
    delivery_message = fields.Char(readonly=True)
    show_force = fields.Boolean()
    is_force = fields.Boolean(string="Force")
    total_worklog_qty = fields.Float(string="Total Worklog Qty")

    # @api.constrains('date_start', 'date_end')
    # def _constrains_dates_coherency(self):
    #     for rec in self:
    #         if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
    #             raise UserError(_('The date to cannot be earlier than the date from.'))
    def action_post(self):
        function_call = self.env.context.get('call_from', False)
        if function_call == 'button_finish':
            self.workorder_id.button_finish()
        elif function_call == 'do_finish':
            self.workorder_id.do_finish()
        elif function_call == 'record_production':
            self.workorder_id.record_production()
        elif function_call == 'action_next':
            self.workorder_id.action_next()

    def action_add_qty(self):
        if self.date_start > datetime.now():
            raise UserError(_('The start date cannot be earlier than the current date.'))

        function_call = self.env.context.get('call_from', False)
        timeline_obj = self.env['mrp.workcenter.productivity']
        domain = [
            ('workorder_id', 'in', self.workorder_id.ids),
        ]

        timeline = timeline_obj.search(domain)

        producing_qty = sum(timeline.mapped('produced_qty')) + self.qty

        if producing_qty > self.workorder_id.qty_production and self.workorder_id.qty_production != 0 and not self.is_force:
            msg = "Producing qty in greater then workorder qty"
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'wo.produced.qty.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(self.env.ref('sd_mrp_wo_split.wo_produced_qty_wizard_view').id, 'form')],
                'name': _('Productivity'),
                'target': 'new',
                'context':{
                    'default_workorder_id': self.workorder_id.id,
                    'default_doall': True,
                    'default_show_force': True,
                    'default_date_start': self.date_start,
                    'call_from': function_call,
                    'default_qty': self.qty,
                    'default_delivery_message': msg
                }
            }

        if producing_qty > self.workorder_id.qty_production:
            raise UserError('You cannot add consumed qty greater then production qty {}'.format(self.workorder_id.qty_production))

        domain = [
            ('workorder_id', 'in', self.workorder_id.ids),
            ('date_end', '=', False),
            ('is_added_qty', '=', False),
            ('user_id', '=', self.env.user.id)
        ]
        timeline = timeline_obj.search(domain)
        if timeline:
            timeline_date_start = timeline[0].date_start
            emp_id = self.env['hr.employee'].sudo().search([('barcode', '=', self.badge_number)])
            if len(emp_id) == 1:
                timeline.write({'employee_id': emp_id.id})

            timeline.write({
                    'produced_qty': self.qty,
                    'is_added_qty': True,
                    'produced_range': self.produced_range,
                    'badge_number': self.badge_number,
                    'date_start': self.date_start,
                })

        if function_call == 'button_finish':
            self.workorder_id.qty_producing = producing_qty
            self.workorder_id._onchange_qty_producing()
            # self.workorder_id.pqty_producing = producing_qty
            self.workorder_id.button_finish()
        elif function_call == 'button_pending':
            self.workorder_id.qty_producing = producing_qty
            self.workorder_id._onchange_qty_producing()
            self.workorder_id.with_context(start_date=timeline_date_start).button_pending()
        elif function_call == 'do_finish':
            if self.workorder_id.qty_production == producing_qty:
                self.workorder_id.qty_producing = producing_qty
                self.workorder_id._onchange_qty_producing()
                self.workorder_id.do_finish()
            else:
                self.workorder_id.qty_producing = producing_qty
                self.workorder_id._onchange_qty_producing()
                self.workorder_id.record_production()
        elif function_call == 'record_production':
            # self.workorder_id.qty_producing = producing_qty
            # self.workorder_id._onchange_qty_producing()
            self.workorder_id.record_production()
        elif function_call == 'action_next':
            self.workorder_id.qty_producing = producing_qty
            self.workorder_id._onchange_qty_producing()
            self.workorder_id.action_next()
