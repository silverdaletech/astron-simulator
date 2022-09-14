# -*- coding: utf-8 -*-
from odoo import models, fields
import odoo
class AuditAddonsListWizard(models.TransientModel):
    _name = 'audit.addons.list.wizard'
    _description = 'Update Addons Wizard'
    def action_update_addons_list(self):
        """
        """

        addons = self.env['audit.addons.list']
        addons.search([]).unlink()

        path_list = odoo.addons.__path__
        for path in path_list:
            addons.create({'name':path})
