from odoo import models, api, fields, _

class Picking(models.Model):
    _inherit = "stock.picking"

    equipment_count = fields.Integer(compute="_compute_equipment_count")
    
    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = len(rec.move_lines.mapped('equipment_ids'))

    def action_view_equipment(self):
        """ This function returns an action that display equipments related to
        picking orders. It can either be a in a list or in a form
        view, if there is only one equipment to show.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("maintenance.hr_equipment_action")
        equipments = self.move_lines.mapped('equipment_ids')
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
    
    def link_equipment_bill(self, move_line_ids):
        for ml in move_line_ids:
            limit = int(ml.quantity)
            for i in range(limit):
                ml_equipment = self.env['maintenance.equipment'].search(
                    [
                        ('account_move_line_id','=',False),
                        ('purchase_order_line_id','=',ml.purchase_line_id.id),
                    ], limit=1
                )
                if ml_equipment:
                    ml_equipment.write({'account_move_line_id':ml.id})
                    ml.is_equipment_created = True
                
                asset_ids = ml.asset_ids
                
                account_id = ml.account_id
                
            if asset_ids:
                if not account_id.multiple_assets_per_line and len(asset_ids) == 1:
                    ml.equipment_ids.write({'asset_id': asset_ids})
                elif account_id.multiple_assets_per_line:
                    for asset in asset_ids:
                        equipment = self.env['maintenance.equipment'].search(
                        [
                            ('account_move_line_id','=',ml.id),
                            ('asset_id','=',False),
                        ], limit=1
                        )
                        if equipment:
                            equipment.asset_id = asset.id

    def _action_done(self):
        res = super(Picking, self)._action_done()
        exp = (lambda x:x.picking_code == 'incoming' and x.product_id.is_equipment and x.purchase_line_id and x.is_equipment_created == False)
        for rec in self.move_lines.filtered(exp):
            if rec.company_id.purchase_equipment == 'receipt':
                
                equipment = self.env['maintenance.equipment'].sudo()
                product = rec.product_id
                values = {
                    'name': product.name,
                    'category_id': product.equipment_category.id if product.equipment_category else False,
                    'maintenance_team_id': product.maintenance_team_id.id if product.maintenance_team_id else False,
                    'technician_user_id': product.technician_user_id.id if product.technician_user_id else False,
                    'partner_id': self.partner_id.id if self.partner_id else False,
                    'stock_move_id': rec.id,
                    'partner_ref': rec.purchase_line_id.order_id.partner_ref,
                    'cost': rec.purchase_line_id.price_unit,
                    'purchase_order_line_id':rec.purchase_line_id.id,
                    'note': rec.purchase_line_id.name
                }
                limit = int(rec.quantity_done)
                for i in range(limit):
                    equipment.create(values)
                    rec.purchase_line_id.is_equipment_created = True
                    rec.is_equipment_created = True

                self.link_equipment_bill(rec.purchase_line_id.invoice_lines)

        return res
