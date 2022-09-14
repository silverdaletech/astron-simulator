from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    equipment_ids = fields.One2many('maintenance.equipment','purchase_order_line_id')
    is_equipment_created = fields.Boolean(string="Equipment Created")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    equipment_count = fields.Integer(compute="_compute_equipment_count")
    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = len(rec.order_line.mapped('equipment_ids'))

    def action_view_equipment(self):
        """ This function returns an action that display equipments related to
        purchase orders. It can either be a in a list or in a form
        view, if there is only one equipment to show.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("maintenance.hr_equipment_action")
        equipments = self.order_line.mapped('equipment_ids')
        if len(equipments) > 1:
            action['domain'] = [('id', 'in', equipments.ids)]
        elif equipments:
            form_view = [(self.env.ref('maintenance.hr_equipment_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = equipments.id
        action['context'] = dict(self._context, create=False)
        return action