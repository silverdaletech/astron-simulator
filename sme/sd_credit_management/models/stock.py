from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _hold_picking_search(self, operator, value):
        recs = self.search([]).filtered(lambda x: x.hold_delivery_till_payment is True)
        if recs:
            return [('id', 'in', [x.id for x in recs])]

    hold_delivery_till_payment = fields.Boolean(default=False, copy=False, compute="_check_delivery_hold",
                                                string="Hold Delivery", help="If True, then holds the DO until  \
                                    invoices are paid and equals to the total amount on the SO",
                                                search=_hold_picking_search)

    def button_validate(self):
        """
        This function will hold to validate delivery if delivery is hold on sale ordr due to credit limit
        """
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                return picking.show_do_hold_warning()
            if partner.credit_hold and not self._context.get('website_order_tx', False):
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit hold.'))
        return super(StockPicking, self).button_validate()

    def action_confirm(self):
        """
             This function will hold to confirm delivery if delivery is hold from sale ordr due to credit limit
             """
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                if picking._context.get('hold_do'):
                    return picking.show_do_hold_warning()
                else:
                    return
            if partner.credit_hold and not self._context.get('website_order_tx', False):
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit hold.'))
        return super(StockPicking, self).action_confirm()

    def action_assign(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                return
            if partner.credit_hold and not self._context.get('website_order_tx', False):
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit hold.'))
        return super(StockPicking, self).action_assign()

    def _check_delivery_hold(self):
        """
        This function will check either we need to hold delivery or not ,Delivery will remain hold till payment
        """
        for picking in self:
            if picking.sale_id.hold_delivery_till_payment and not picking.sale_id.check_invoice_fully_paid():
                if picking.picking_type_id.code == 'outgoing':
                    picking.hold_delivery_till_payment = True
                else:
                    picking.hold_delivery_till_payment = False
            elif picking.sale_id.hold_delivery_till_payment and picking.sale_id.check_invoice_fully_paid():
                picking.hold_delivery_till_payment = False
            else:
                picking.hold_delivery_till_payment = False

    def show_do_hold_warning(self):
        """Raise user warning if the invoice(s) is/are not fully paid."""
        raise UserError(_("Delivery is on hold due to non payment."))


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_moves_to_assign_domain(self, company_id):
        """ This method adds hold delivery domain to restrict while checking
        availability during the scheduler run"""
        hold_do_picking = self.env['stock.move'].search([]).filtered(
            lambda x: x.picking_id.hold_delivery_till_payment == True)
        domain = super(ProcurementGroup, self)._get_moves_to_assign_domain(company_id)
        domain = expression.AND([domain, [('id', 'not in', hold_do_picking.ids)]])
        return domain
