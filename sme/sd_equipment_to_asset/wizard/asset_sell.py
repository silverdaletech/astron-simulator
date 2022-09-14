# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError

class AssetSell(models.TransientModel):
    _inherit = 'account.asset.sell'

    def do_action(self):
        record = super(AssetSell, self).do_action()
        for lines in self.asset_id:
            for line in  lines.equipment_ids:
                if line.workcenter_id and line.workcenter_id.active:
                    raise ValidationError(_(
                        "{} equipment attached to this asset has a workcenter, kindly archive {} work center."
                    .format(
                        line.name,
                        line.workcenter_id.name
                        )
                    ))
            lines.equipment_ids.sudo().write({
                'is_dispose': True
            })
        return record