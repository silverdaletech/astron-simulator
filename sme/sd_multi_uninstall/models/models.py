# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IrModule(models.Model):
    _inherit = "ir.module.module"

    def multiple_module_uninstall(self):
        """
            Function called from server action to uninstall multiple modules
        """
        modules = self.browse(self.env.context.get('active_ids')).button_immediate_uninstall()

