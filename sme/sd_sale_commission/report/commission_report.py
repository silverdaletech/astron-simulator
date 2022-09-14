# Copyright (C) 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import fields, models, tools


class ActivityReport(models.Model):
    """ Sale Commission Analysis """

    _name = "sale.commission.report"
    _auto = False
    _description = "Sale Commssion Analysis"

    product_id = fields.Many2one('product.product',string="Product")
    unit_price = fields.Float(string="Unit Price")
    qty = fields.Float(stirng="Quantity")
    # uom_id = fields.Many2one('',stirng="UOM")
    subtotal = fields.Float (stirng="Subtotal")
    commissionable_amount = fields.Float(stirng="Commissionable Amount")
    commission_amount = fields.Float(stirng="Commission Amount")
    # commission_record_id = fields.Float('sale.commission.record')
    agent_id = fields.Many2one('sale.commission.agent')
    # state = fields.Selection([
    #                         ('pending', 'Pending'),
    #                         ('bill_created', 'Bill Created'),
    #                         ],default='pending',
    #                         stirng="Settlement status")
                # l.commissionable_amount,
                # l.commission_amount,
                # l.commission_record_id,
    def _select(self):
        return """
            SELECT
                l.id,
                l.product_id,
                l.unit_price,
                l.qty,
                l.subtotal,
                l.agent_id,
                l.commissionable_amount,
                l.commission_amount
        """

    def _from(self):
        return """
            FROM sale_commission_line AS l
        """

    def _join(self):
        return """
            JOIN crm_lead_line AS ll ON l.id = ll.lead_id
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
            )
        """,
            (
                AsIs(self._table),
                AsIs(self._select()),
                AsIs(self._from())
            ),
        )
