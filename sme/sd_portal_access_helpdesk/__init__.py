# -*- coding: utf-8 -*-

from . import controllers
from . import models

from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    """ This method will remove all the server actions used for 'Merge Action' in the contextual menu. """
    env = api.Environment(cr, SUPERUSER_ID, {})
    modules_to_upgrade = env['ir.module.module'].search([('name', '=', 'helpdesk')])
    modules_to_upgrade.button_upgrade()