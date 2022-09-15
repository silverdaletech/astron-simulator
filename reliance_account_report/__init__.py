# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def uninstall_hook(cr, registry):
    """
        this hook will update sale app when
        reliance_account_report module will be uninstalled ever.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    modules_to_upgrade = env['ir.module.module'].search([('name', '=', 'sale')])
    modules_to_upgrade.button_upgrade()
