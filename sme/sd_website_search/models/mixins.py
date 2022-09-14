# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request


class WebsiteSearchableMixin(models.AbstractModel):
    """Mixin to be inherited by all models that need to searchable through website"""
    _inherit = 'website.searchable.mixin'

    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        fields = search_detail['search_fields']
        base_domain = search_detail['base_domain']
        domain = self._search_build_domain(base_domain, search, fields, search_detail.get('search_extra'))
        if self == self.env['product.public.category']:
            domain.append(('website_id', '=', request.website.id))
        model = self.sudo() if search_detail.get('requires_sudo') else self
        results = model.search(
            domain,
            limit=limit,
            order=search_detail.get('order', order)
        )
        count = model.search_count(domain)
        return results, count
