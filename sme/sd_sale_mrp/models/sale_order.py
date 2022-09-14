from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    """ This will use to update project description from sale order line
            """
    _inherit = 'sale.order.line'

    mo_description = fields.Html(
        string='MO Description',
        required=False)
    is_mo_description_active = fields.Boolean(
        string='Is_mo_description_active', compute='compute_is_mo_description_active',
        required=False)
    
    # This fields copied from sale_project
    is_service = fields.Boolean("Is a Service", compute='_compute_is_service', store=True, compute_sudo=True, help="Sales Order item should generate a task and/or a project, depending on the product settings.")

    @api.depends('product_id')
    def _compute_is_service(self):
        for so_line in self:
            so_line.is_service = so_line.product_id.type == 'service'

    def compute_is_mo_description_active(self):
        for rec in self:
            rec.is_mo_description_active = False
            is_active = self.env['ir.config_parameter'].sudo().get_param('sd_sale_mrp.is_mo_description')
            if is_active:
                rec.is_mo_description_active = True

    def update_view_mo_description(self):
        """ This will open view of sale
                    """
        for line in self:
            return {
                'name': _('Sale Line'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order.line',
                'res_id': line.id,
                'views': [(self.env.ref('sd_sale_mrp.view_custom_sale_line_form').id, 'form')],
                'target': 'new',
            }


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        res = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin,
                                                      company_id, values, bom)
        if values.get('mo_notes', False):
            res.update({
                'mo_notes': values.get('mo_notes', False),
            })
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        if self.sale_line_id.mo_description:
            if self.env['ir.config_parameter'].sudo().get_param('sd_sale_mrp.is_mo_description'):
                res.update({
                    'mo_notes': self.sale_line_id.mo_description,
                })
        return res


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mo_notes = fields.Html(string='Notes', tracking=True)
