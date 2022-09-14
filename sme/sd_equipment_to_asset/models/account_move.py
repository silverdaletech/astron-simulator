import re
from odoo import fields, models, api, _
from odoo.tools.sql import rename_column


class AccountMove(models.Model):
    _inherit = 'account.move'
    equipment_count = fields.Integer(compute="_compute_equipment_count")

    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = len(rec.invoice_line_ids.mapped('equipment_ids'))

    def action_view_equipment(self):
        """ This function returns an action that display equipments related to
        picking orders. It can either be a in a list or in a form
        view, if there is only one equipment to show.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("maintenance.hr_equipment_action")
        equipments = self.invoice_line_ids.mapped('equipment_ids')
        if len(equipments) > 1:
            action['domain'] = [('id', 'in', equipments.ids)]
        elif equipments:
            form_view = [(self.env.ref('maintenance.hr_equipment_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = equipments.id
        action['context'] = dict(self._context, create=False)
        return action

    def _create_equipments(self):
        pe_type = self.company_id.purchase_equipment
        exp = (lambda x: x.purchase_line_id and x.product_id.is_equipment)
        for rec in self.invoice_line_ids.filtered(exp):
            requipment = self.env['maintenance.equipment'].sudo()
            limit = int(rec.quantity)
            if pe_type == 'bill' and not rec.is_equipment_created:
                for i in range(limit):
                    product = rec.product_id
                    values = {
                        'name': rec.product_id.name,
                        'category_id': product.equipment_category.id if product.equipment_category else False,
                        'maintenance_team_id': product.maintenance_team_id.id if product.maintenance_team_id else False,
                        'technician_user_id': product.technician_user_id.id if product.technician_user_id else False,
                        'partner_id': self.partner_id.id if self.partner_id else False,
                        'partner_ref': rec.purchase_line_id.order_id.partner_ref,
                        'cost': rec.purchase_line_id.price_unit,
                        'purchase_order_line_id': rec.purchase_line_id.id,
                        'account_move_line_id': rec.id,
                        'note': rec.purchase_line_id.name
                    }
                    requipment.create(values)
                    rec.purchase_line_id.is_equipment_created = True
                    rec.is_equipment_created = True
            elif pe_type == 'receipt':
                for i in range(limit):
                    equipment = self.env['maintenance.equipment'].search(
                        [
                            ('account_move_line_id', '=', False),
                            ('purchase_order_line_id', '=', rec.purchase_line_id.id),
                        ], limit=1
                    )
                    if equipment:
                        equipment.write({'account_move_line_id': rec.id})
                        rec.is_equipment_created = True
            asset_ids = rec.asset_ids
            account_id = rec.account_id
            if asset_ids:
                if not account_id.multiple_assets_per_line and len(asset_ids) == 1:
                    rec.equipment_ids.write({'asset_id': asset_ids})
                elif account_id.multiple_assets_per_line:
                    for asset in asset_ids:
                        equipment = self.env['maintenance.equipment'].search(
                            [
                                ('account_move_line_id', '=', rec.id),
                                ('asset_id', '=', False),
                            ], limit=1
                        )
                        if equipment:
                            equipment.asset_id = asset.id

    def _post(self, soft=True):
        posted = super(AccountMove, self)._post(soft)

        for bill in posted.filtered(lambda x: x.move_type == 'in_invoice'):
            if self.company_id.purchase_equipment:
                bill._create_equipments()

        return posted


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    equipment_ids = fields.One2many('maintenance.equipment', 'account_move_line_id')
    is_equipment_created = fields.Boolean(string="Equipment Created")
