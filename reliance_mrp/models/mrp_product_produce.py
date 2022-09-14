# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    def action_generate_serial(self):
        Lot = self.env['stock.production.lot'].sudo()
        notions = ['P', 'L', 'S']
        component_lot_names = dict.fromkeys(notions, [])
        # line_ids = self.move_raw_ids.filtered(lambda line: line.product_id and line.product_id.tracking == 'lot' and line.qty_done)
        line_ids = self.move_raw_ids.move_line_ids.filtered(lambda line: line.product_id and line.product_id.tracking == 'lot' and line.qty_done)
        assign_lines = line_ids.filtered(lambda line: line.product_id and line.product_id.tracking and line.product_id.lot_prefix == 'M')
        if not assign_lines:
            if len(line_ids) == 1:
                # if there is only one component with the lot number
                lot_name = line_ids.lot_id.name
                lot_id = Lot.search([('name', '=', lot_name), ('product_id', '=', self.product_id.id)])
                if lot_id.id:
                    self.lot_producing_id = lot_id.id
                else:
                    self.lot_producing_id = Lot.create({'name': lot_name, 'product_id': self.product_id.id, 'company_id': self.company_id.id}).id
            elif len(line_ids) > 1:
                # if there are more components with lot numbers
                for consume_line in line_ids:
                    if not consume_line.product_id.lot_prefix:
                        raise ValidationError("Please set Lot prefix for the product: '%s'." % (consume_line.product_id.display_name))
                    if not consume_line.lot_id:
                        raise ValidationError("Please provide Lot for product: '%s'." % (consume_line.product_id.display_name))
                    component_lot_names[consume_line.product_id.lot_prefix] = component_lot_names[consume_line.product_id.lot_prefix] + ['%s%s%s' % (consume_line.product_id.lot_prefix,(consume_line.product_id.lot_shade + '.') if consume_line.product_id.lot_shade else '', consume_line.lot_id.name)]

                lot_names = []
                for notion in notions:
                    lots = component_lot_names[notion]
                    name = '--'.join(lots)
                    if name != '':
                        lot_names.append(name)
                lot_name = '--'.join(lot_names)
                lot_id = Lot.search([('name', '=', lot_name), ('product_id', '=', self.product_id.id)])
                if lot_id.id:
                    self.lot_producing_id = lot_id.id
                else:
                    self.lot_producing_id = Lot.create({'name': lot_name, 'product_id': self.product_id.id, 'company_id': self.company_id.id}).id
        else:
            raise ValidationError('Lot number cannot be generated, please assign lot number manually.')
        # action_data = self.env.ref('mrp.act_mrp_product_produce').read()[0]
        # action_data['res_id'] = self.id
        # action_data['context'] = {'default_lot_id': self.finished_lot_id.id}
        # action = action_data