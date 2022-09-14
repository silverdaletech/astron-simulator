import math
from operator import itemgetter
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SplitOrderWizard(models.TransientModel):
    _name = 'split.order.wizard'
    _description = 'Split mrp order wizard'

    def _current_mo_date(self):
        active_production_id = self.env.context.get('active_id')
        production = self.env['mrp.production'].browse(active_production_id)
        return production.date_planned_start

    def _total_mo_quantity(self):
        active_production_id = self.env.context.get('active_id')
        production = self.env['mrp.production'].browse(active_production_id)
        return production.product_qty

    split_into = fields.Integer(string="Split Order Into")
    date_planned = fields.Datetime('Scheduled Date', default=_current_mo_date,
                                   help="Date at which you plan to start the production, this can not be lee than the "
                                        "original MO schedual date.")
    split_line_ids = fields.One2many('split.order.line.wizard', 'split_id', string='Split Lines')
    total_quantity = fields.Float(string='Original MO Quantity', default=_total_mo_quantity)

    @api.onchange('split_into')
    def onchange_split_into(self):
        if self.split_into:
            for rec in self:
                lines = []
                for line in range(rec.split_into):
                    vals = {
                        'line_date_planned': rec.date_planned,
                        'quantity': rec._get_quantity(line),
                        'is_original': rec.is_original(line),
                        'ratio': rec._get_quantity(line) / self.total_quantity,
                    }
                    lines.append((0, 0, vals))
                rec.split_line_ids = False
                rec.write({'split_line_ids': lines})

    def is_original(self, line):
        split_obj = self._calculate_split_count_obj()
        if split_obj['add_to_product_qty'] != split_obj['split_count'] and line == 0:
            return True
        else:
            return False

    def _get_quantity(self, line):
        split_obj = self._calculate_split_count_obj()
        if split_obj['add_to_product_qty'] != split_obj['split_count'] and line == 0:
            return split_obj['add_to_product_qty']
        else:
            return split_obj['split_count']

    def action_split_mo(self):
        split_count, mrp_production_id, production_qty, mo_date_planned = itemgetter('split_count', 'production',
                                                                                     'production_qty',
                                                                                     'date_planned_start')(
            self._calculate_split_count_obj())
        total_lines_qty = 0
        for rec in self.split_line_ids:
            total_lines_qty = total_lines_qty + rec.quantity

        if total_lines_qty != self.total_quantity:
            raise UserError(_(
                f'Sum of split quantities must match exactly with total original qty, '
                f'please adjust {self.total_quantity - total_lines_qty} quantity in lines.',
            ))

        if self.split_into not in range(2, int(production_qty) // 2):
            raise UserError(_(
                f"Split number must be greater than 1 and less than {int(production_qty) // 2}.",
            ))

        values = []
        for rec in self.split_line_ids:
            vals = {
                'date': rec.line_date_planned,
                'quantity': rec.quantity,
                'split_into': self.split_into,
                'is_original': rec.is_original,
                'total_quantity': self.total_quantity,
                'ratio': rec.quantity / self.total_quantity, 
            }
            values.append(vals)
        return mrp_production_id.with_context(mo_id_to_split=mrp_production_id, values=values, ).split_mrp_production()

    def _calculate_split_count_obj(self):
        active_production_id = self.env.context.get('active_id')
        production = self.env['mrp.production'].browse(active_production_id)
        production_qty = production.product_qty
        split_into = self.split_into
        date_planned_start = production.date_planned_start

        if self.split_into not in range(2, int(production_qty)):
            raise UserError(_(
                f"Input should be greater than 1 and less than {production_qty}",
            ))

        split_count = production_qty / split_into
        split_count = math.floor(split_count * 10 ** 2) / 10 ** 2
        split_count = math.trunc(split_count)
        add_to_product_qty = split_count
        difference_in_qty = production_qty - (split_count * split_into)
        # difference_in_qty = math.trunc(difference_in_qty)
        if difference_in_qty:
            add_to_product_qty = split_count + difference_in_qty

        return {
            'split_count': split_count,
            'production': production,
            'production_qty': production_qty,
            'add_to_product_qty': add_to_product_qty,
            'date_planned_start': date_planned_start,
        }


class SplitOrderLinesWizard(models.TransientModel):
    _name = 'split.order.line.wizard'
    _description = 'Split mrp order line wizard'

    split_id = fields.Many2one('split.order.wizard', string='Split Order Reference', ondelete='set null')
    line_date_planned = fields.Datetime(string='Split Date Planned',
                                        help="Default date will be the original date in the MO ")
    quantity = fields.Float(string="Split Quantity")
    is_original = fields.Boolean('Original', default=False)
    ratio = fields.Float()

    @api.onchange('line_date_planned')
    def onchange_line_date_planned(self):
        active_production_id = self.env.context.get('active_id')
        production = self.env['mrp.production'].browse(active_production_id)
        date_planned_start = production.date_planned_start
        date_deadline = production.date_deadline
        if date_deadline:
            if self.line_date_planned > date_deadline:
                raise UserError(_(
                    f'Scheduled Date can not be greater than parent MO Deadline Date, {date_deadline}',
                ))
        if self.line_date_planned and date_planned_start:
            if self.line_date_planned < date_planned_start:
                raise UserError(_(
                    f'Scheduled Date can not be less than parent MO Scheduled Date, {date_planned_start}',
                ))
