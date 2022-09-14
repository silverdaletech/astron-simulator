
from odoo import models, fields, api, _


class SdSaleOrderWizard(models.TransientModel):
    _name = 'sd.sale.order.wizard'
    _description = 'Sale Order wizard'

    def _default_order(self):
        return self.env.context.get('active_id')

    order_id = fields.Many2one('sale.order', string="Sale Order", default=_default_order)
    order_line = fields.Many2one('sale.order.line', string="Order Lines")

    def action_create_analytic_lines(self):
        if self.order_line:
            self.order_line.create_timesheet()
