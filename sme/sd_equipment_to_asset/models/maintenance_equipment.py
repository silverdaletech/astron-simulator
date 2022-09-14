from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    purchase_order_line_id = fields.Many2one('purchase.order.line')
    account_move_line_id = fields.Many2one('account.move.line')
    stock_move_id = fields.Many2one('stock.move')
    asset_id = fields.Many2one('account.asset')
    is_dispose = fields.Boolean()

    def unlink(self):
        for line in self:
            if line.asset_id:
                raise ValidationError(_(
                    "Cannot Delete/Archive equipment without deleting/archiving the asset first."
                ))
        return super(MaintenanceEquipment, self).unlink()

    def action_archive(self):
        for line in self:
            if line.asset_id:
                raise ValidationError(_(
                    "Cannot Delete/Archive equipment without deleting/archiving the asset first."
                ))
        return super(MaintenanceEquipment, self).action_archive()
