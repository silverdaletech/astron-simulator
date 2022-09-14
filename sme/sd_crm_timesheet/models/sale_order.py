from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            if rec.analytic_account_id:
                if rec.order_line:
                    for line in rec.order_line:
                        if line.analytic_line_ids.account_id:
                            line.analytic_line_ids.account_id = rec.analytic_account_id.id

        return res

    def action_link_crm_timesheet(self):
        """ This will open view of sale
                    """
        # self.ensure_one()
        for line in self.order_line:
            return {
                'name': _('Order Wizard'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sd.sale.order.wizard',
                'context': {'order_id': self.id},
                'target': 'new',
            }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def create_timesheet(self):
        for rec in self:
            if rec.order_id and rec.order_id.opportunity_id and rec.order_id.opportunity_id.timesheet_ids:
                timesheets = []
                total = 0.0
                for timesheet in rec.order_id.opportunity_id.timesheet_ids:
                    if timesheet:
                        timesheets.append((4, timesheet.id))
                        rec.write({'analytic_line_ids': timesheets})
                        total += timesheet.unit_amount
                        rec.update({
                            'qty_delivered': total,
                        })
