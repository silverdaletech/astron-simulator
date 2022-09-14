# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    """ This will use to update project description from sale order line
            """
    _inherit = 'sale.order.line'

    additional_description = fields.Html(
        string='Description',
        required=False)
    service_tracking = fields.Selection(related='product_id.service_tracking')

    def update_view_description(self):
        """ This will open view of sale
                    """
        for line in self:
            return {
                'name': _('Sale Line'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order.line',
                'res_id': line.id,
                'views': [(self.env.ref('sd_sale_project.view_custom_sale_line_form').id, 'form')],
                'target': 'new',
                'context': {'create': False}
            }

    def write(self, vals):
        """ This will update description on project
            from sale order line description
        """
        write_result = super(SaleOrderLine, self).write(vals)
        for order_line in self:
            if order_line.additional_description:
                if vals.get('project_id'):
                    project = self.env['project.project'].search([('id', '=', vals['project_id'])], limit=1)
                    if project:
                        project.description = order_line.additional_description

        return write_result
