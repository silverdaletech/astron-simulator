from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Add search function
    property_product_pricelist = fields.Many2one(search='_search_property_product_pricelist')

    def _search_property_product_pricelist(self, operator, value):
        """
        search function is changed by silverdale, Previous it was returning partner record from ir_property only,
        but now it will check if pricelist is generic
            then get all partner of current company that has no record in ir_property
            for any other priclist (to get default pricelist contact ),
        if pricelist is not generic then
            return partner that has record for pricelist in ir_property

        :param operator: union operator is use to merge lists
        :param value:
        :return:will return partners
        """
        if operator == '=':
            pricelists = self.env['product.pricelist'].search([('id', operator, value)])
        else:
            pricelists = self.env['product.pricelist'].search([('name', operator, value)])

        pricelist = []
        for item in pricelists.ids:
            pricelist.append('product.pricelist,%s' % str(item))

        # We return an emty list if the pricelist can not be found
        if not pricelist:
            return [('id', '=', False)]

        vals = {
            'pricelist': pricelist,
            # Silverdale Changes : company value change from self.env.user_id.company.id to below
            'company_id': self.env.company.id,
        }
        is_generic = self.env.cr.execute(
            """
            SELECT id
            FROM ir_property
            WHERE name = 'property_product_pricelist'
            AND res_id IS  NULL
            AND value_reference =  ANY(%(pricelist)s)
            AND company_id =  %(company_id)s
            """, vals
        )
        is_generic_property = [r[0] for r in self.env.cr.fetchall()]
        if is_generic_property:
            self.env.cr.execute(
                """
                SELECT
                    REPLACE(res_id, 'res.partner,','')::INT AS id
                FROM ir_property
                WHERE name = 'property_product_pricelist'
                AND res_id IS NOT NULL
                AND value_reference =  ANY(%(pricelist)s)
                AND company_id =  %(company_id)s
                """, vals
            )

            partner_ids = [r[0] for r in self.env.cr.fetchall()]

            self.env.cr.execute(
                """
                SELECT
                    REPLACE(res_id, 'res.partner,','')::INT AS id
                FROM ir_property
                WHERE name = 'property_product_pricelist'
                AND res_id IS NOT NULL
                """, vals
            )

            all_company_property = [r[0] for r in self.env.cr.fetchall()]

            query = f"""
                SELECT id
                FROM res_partner
                WHERE company_id = {vals.get('company_id')}
                OR company_id is Null
                AND active = True
                """

            self.env.cr.execute(query)
            results = self.env.cr.fetchall()

            all_partner_ids = [r[0] for r in results]

            all_company_property_set = set(all_company_property)
            all_partner_ids_set = set(all_partner_ids)

            other_partners = (all_partner_ids_set - all_company_property_set)
            pricelist_applied_partner = set.union(other_partners, set(partner_ids))
            pricelist_applied_partner_list = list(pricelist_applied_partner)
            return pricelist_applied_partner_list and [('id', 'in', pricelist_applied_partner_list)] or [
                ('id', '=', False)]
        else:
            self.env.cr.execute(
                """
                SELECT
                    REPLACE(res_id, 'res.partner,','')::INT AS id
                FROM ir_property
                WHERE name = 'property_product_pricelist'
                AND res_id IS NOT NULL
                AND value_reference =  ANY(%(pricelist)s)
                AND company_id =  %(company_id)s
                """, vals
            )

            partner_ids = [r[0] for r in self.env.cr.fetchall()]

            return partner_ids and [('id', 'in', partner_ids)] or [('id', '=', False)]


