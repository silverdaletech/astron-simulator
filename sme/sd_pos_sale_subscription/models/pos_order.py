# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.misc import parse_date
from odoo.tools import is_html_empty
import re


class PosOrder(models.Model):
    _inherit = "pos.order"

    subscription_count = fields.Integer(compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        """Compute the number of distinct subscriptions linked to the order."""
        for order in self:
            sub_count = 0
            if order.config_id.allow_pos_subscriptions:
                sub_count = len(self.env['pos.order.line'].read_group([('order_id', '=', order.id), ('subscription_id', '!=', False)],
                                                        ['subscription_id'], ['subscription_id']))
            order.subscription_count = sub_count

    @api.model
    def create(self, vals):
        """
        Create a sales order if there is a subscription product in pos order lines.
        """
        res = super(PosOrder, self).create(vals)
        if res and res.config_id.allow_pos_subscriptions:
            subscription_line_ids = res.lines.filtered(lambda l: l.product_id.recurring_invoice)
            if subscription_line_ids:
                res.create_subscriptions()
        return res

    def _generate_pos_order_invoice(self):
        """
        Call super and link the generated invoice with sales order.
        """
        res = super(PosOrder, self)._generate_pos_order_invoice()
        for order in self:
            if order.account_move and order.config_id.allow_pos_subscriptions:
                recurring_invoice_lines = order.account_move.invoice_line_ids.filtered(lambda l: l.product_id.recurring_invoice)
                if recurring_invoice_lines:
                    for line in recurring_invoice_lines:
                        sub_pos_lines = order.lines.filtered(lambda l: l.product_id == line.product_id and l.product_id.recurring_invoice)
                        for pos_line in sub_pos_lines:
                            vals = pos_line._prepare_subscription_values()
                            if vals:
                                line.write({
                                    'subscription_id': vals.get('subscription_id', False),
                                    'subscription_start_date': vals.get('subscription_start_date', False),
                                    'subscription_end_date': vals.get('subscription_end_date', False),
                                    'analytic_account_id': vals.get('analytic_account_id', False),
                                })
        return res

    def _prepare_subscription_data(self, template):
        """Prepare a dictionnary of values to create a subscription from a template."""
        self.ensure_one()
        date_today = fields.Date.context_today(self)
        recurring_invoice_day = date_today.day
        recurring_next_date = self.env['sale.subscription']._get_recurring_next_date(
            template.recurring_rule_type, template.recurring_interval,
            date_today, recurring_invoice_day
        )
        values = {
            'name': template.name,
            'template_id': template.id,
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'date_start': fields.Date.context_today(self),
            'description': self.note if not is_html_empty(self.note) else template.description,
            'pricelist_id': self.pricelist_id.id,
            'recurring_next_date': recurring_next_date,
            'recurring_invoice_day': recurring_invoice_day,
        }
        default_stage = self.env['sale.subscription.stage'].search([('category', '=', 'progress')], limit=1)
        if default_stage:
            values['stage_id'] = default_stage.id
        return values

    def create_subscriptions(self):
        """
        Create subscriptions based on the products' subscription template.

        Create subscriptions based on the templates found on lines' products. Note that only
        lines not already linked to a subscription are processed; one subscription is created per
        distinct subscription template found.
        
        When subscription is created, call generate_unique_license_key method to generate licence key.

        :return: ids of newly create subscriptions
        """
        res = []
        for order in self:
            to_create = order._split_subscription_lines()
            # create a subscription for each template with all the necessary lines
            for template in to_create:
                values = order._prepare_subscription_data(template)
                values['recurring_invoice_line_ids'] = to_create[template]._prepare_subscription_line_data()
                subscription = self.env['sale.subscription'].sudo().create(values)
                subscription.onchange_date_start()
                res.append(subscription.id)
                to_create[template].write({'subscription_id': subscription.id})
                subscription.message_post(
                        body=_(f'This subscription has been created from: POS Order(ID:{order.id})'),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note')
                self.env['sale.subscription.log'].sudo().create({
                    'subscription_id': subscription.id,
                    'event_date': fields.Date.context_today(self),
                    'event_type': '0_creation',
                    'amount_signed': subscription.recurring_monthly,
                    'recurring_monthly': subscription.recurring_monthly,
                    'currency_id': subscription.currency_id.id,
                    'category': subscription.stage_category,
                    'user_id': order.user_id.id,
                })
        return res

    def _split_subscription_lines(self):
        """Split the line according to subscription templates that must be created."""
        self.ensure_one()
        res = dict()
        new_sub_lines = self.lines.filtered(lambda l: not l.subscription_id and l.product_id.subscription_template_id and l.product_id.recurring_invoice)
        templates = new_sub_lines.mapped('product_id').mapped('subscription_template_id')
        for template in templates:
            lines = self.lines.filtered(lambda l: l.product_id.subscription_template_id == template and l.product_id.recurring_invoice)
            res[template] = lines
        return res

    def action_open_subscriptions(self):
        """Display the linked subscription and adapt the view to the number of records to display."""
        self.ensure_one()
        subscriptions = self.lines.mapped('subscription_id')
        action = self.env["ir.actions.actions"]._for_xml_id("sale_subscription.sale_subscription_action")
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        elif len(subscriptions) == 1:
            form_view = [(self.env.ref('sale_subscription.sale_subscription_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscriptions.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = dict(self._context, create=False)
        return action


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    subscription_id = fields.Many2one('sale.subscription', 'Subscription', copy=False)

    def _prepare_subscription_values(self):
        """
        Display the invoicing period in the invoice line description, link the invoice line to the
        correct subscription and to the subscription's analytic account if present, add revenue dates.
        """
        res = {}
        if self.subscription_id:
            res.update(subscription_id=self.subscription_id.id)
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            next_date = self.subscription_id.recurring_next_date
            previous_date = next_date - relativedelta(**{periods[self.subscription_id.recurring_rule_type]: self.subscription_id.recurring_interval})
            is_already_period_msg = True if _("Invoicing period") in self.name else False
            date_start, date_start_display, date_end = None, None, None
            if is_already_period_msg:
                try:
                    regexp = _("Invoicing period") + ": (.*) - (.*)"
                    match = re.search(regexp, self.name)
                    date_start = parse_date(self.env, match.group(1))
                    date_start_display = date_start
                    date_end = parse_date(self.env, match.group(2))
                except AttributeError:
                    # Fallback on discount
                    pass
            if not date_start or not date_start_display or not date_end:
                # here we have a slight problem: the date used to compute the pro-rated discount
                # (that is, the date_from in the upsell wizard) is not stored on the line,
                # preventing an exact computation of start and end revenue dates
                # witness me as I try to retroengineer the ~correct dates 🙆‍
                # (based on `partial_recurring_invoice_ratio` from the sale.subscription model)
                total_days = (next_date - previous_date).days
                days = round((1 - self.discount / 100.0) * total_days)
                date_start = next_date - relativedelta(days=days+1)
                date_start_display = next_date - relativedelta(days=days)
                date_end = next_date - relativedelta(days=1)
            res.update({
                'subscription_start_date': date_start,
                'subscription_end_date': date_end,
            })
            if self.subscription_id.analytic_account_id:
                res['analytic_account_id'] = self.subscription_id.analytic_account_id.id
        return res

    def _prepare_subscription_line_data(self):
        """Prepare a dictionnary of values to add lines to a subscription."""
        values = list()
        for line in self:
            values.append((0, False, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.qty,
                'uom_id': line.product_uom_id.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }))
        return values