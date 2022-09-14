# -*- coding: utf-8 -*-

from cgitb import reset
from urllib import response
from odoo import api, fields, models, modules, tools, _, release, SUPERUSER_ID
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.base.models.ir_module import assert_log_admin_access
import datetime
import requests
import logging
from odoo.tools import misc, ustr
from . import config

_logger = logging.getLogger(__name__)
limit_date = datetime.date.today()
limit_date_str = limit_date.strftime(misc.DEFAULT_SERVER_DATE_FORMAT)


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def get_silverdale_apps(self):
        sd_modules = 0
        modules_installed = 0
        modules_not_installed = 0
        modules = self.sudo().search([('author', '=', 'Silverdale')])
        if modules:
            sd_modules = len(modules)
            modules_installed = len(modules.filtered(lambda m: m.state == 'installed'))
            modules_not_installed = len(modules.filtered(lambda m: m.state == 'uninstalled'))
        return {
            'sd_modules': sd_modules,
            'modules_installed': modules_installed,
            'modules_not_installed': modules_not_installed,
        }

    def get_license_response(self, apps=False):
        data = self._get_silverdale_data(apps)
        arguments = {"data": data}
        url = config.license_url + data.get('key', 'invalid-key')

        response = requests.get(url, json=arguments, timeout=30)
        response = response.json()
        return response

    def sd_silverdale_key(self):
        response = self.get_license_response()
        IrParamSudo = self.env['ir.config_parameter'].sudo().set_param
        if response.get('result', False) and response['result']['status']:
            IrParamSudo('sd_base_setup.sd_license_expire', response['result']['expiry_date'])
            return {
                'status':True,
                'expire_date':response['result']['expiry_date']
            }
        else:
            IrParamSudo('sd_base_setup.sd_license_expire', False)
            return {
                'status': False,
                'expire_date': ''
            }

    @api.model
    def _get_silverdale_data(self, apps=False):
        Users = self.env['res.users'].sudo()
        IrParamSudo = self.env['ir.config_parameter'].sudo()

        dbuuid = IrParamSudo.get_param('database.uuid')
        db_create_date = IrParamSudo.get_param('database.create_date')
        limit_date = datetime.datetime.now()
        limit_date = limit_date - datetime.timedelta(15)
        limit_date_str = limit_date.strftime(misc.DEFAULT_SERVER_DATETIME_FORMAT)
        nbr_users = Users.search_count([('active', '=', True)])
        nbr_active_users = Users.search_count([("login_date", ">=", limit_date_str), ('active', '=', True)])
        nbr_share_users = 0
        nbr_active_share_users = 0
        if "share" in Users._fields:
            nbr_share_users = Users.search_count([
                    ("share", "=", True),
                    ('active', '=', True)
                ])
            nbr_active_share_users = Users.search_count([
                    ("share", "=", True),
                    ("login_date", ">=", limit_date_str),
                    ('active', '=', True)
                ])
        
        user = self.env.user
        domain = [('author', '=', 'Silverdale'), ('state', 'in', ['installed', 'to upgrade', 'to remove'])]
        if not apps:
            apps = self.env['ir.module.module'].sudo().search_read(domain, ['name'])

        sd_license_key = IrParamSudo.get_param('sd_base_setup.sd_license_key', '0000')
        web_base_url = IrParamSudo.get_param('web.base.url')
        
        data = {
            "dbuuid": dbuuid,
            "nbr_users": nbr_users,
            "nbr_active_users": nbr_active_users,
            "nbr_share_users": nbr_share_users,
            "nbr_active_share_users": nbr_active_share_users,
            "db": self._cr.dbname,
            "db_create_date": db_create_date,
            "version": release.version,
            "language": user.lang,
            "url": web_base_url,
            "apps": [app['name'] for app in apps],
            "key": sd_license_key,
        }
        return data

    @assert_log_admin_access
    def button_immediate_install(self):
        """
            odoo base module call when we install any module.
        """
        response = self.get_license_response(apps=self)
        IrParamSudo = self.env['ir.config_parameter'].sudo().set_param
        if response.get('result', False) and response['result']['status']:
            return super(Module ,self).button_immediate_install()
        else:
            raise UserError(_('Your licence key for this Silverdale extension is not valid. You can check your '
                              'subscription here at silverdaletech.com/my/subscription.'))

    @assert_log_admin_access
    def button_immediate_upgrade(self):
        """
            odoo base module call when we upgrade any module.
        """
        response = self.get_license_response(apps=self)
        IrParamSudo = self.env['ir.config_parameter'].sudo().set_param
        if response.get('result', False) and response['result']['status']:
            return super(Module ,self).button_immediate_upgrade()
        else:
            raise UserError(_('Your licence key for this Silverdale Extension is not valid. You can check your '
                              'subscription here at silverdaletech.com/my/subscription.'))

    def inactive_silverdale_module_views(self):
        """
            Inactive silverdale views and menu
        """
        #fixme update functionality in next revision
        pass
        return True
        url = config.applist_url
        response = requests.get(url, json={}, timeout=30)
        response = response.json()
        IrParamSudo = self.env['ir.config_parameter'].sudo()

        expiry_date = IrParamSudo.get_param('sd_base_setup.sd_license_expire', False)
        if not expiry_date or  expiry_date < limit_date_str:
            apps = response['result']['data']
            ir_model_data = self.env['ir.model.data'].sudo().search([('module', '=', apps), ('model', '=', 'ir.ui.view')]).mapped('res_id')
            ir_view = self.env['ir.ui.view'].search([('id', 'in', ir_model_data),('model', '!=', 'res.config.settings')])
            ir_view.inherit_children_ids.write({'active': False})
            ir_view.write({'active': False})
            ir_model_data = self.env['ir.model.data'].search([('module', '=', apps), ('model', '=', 'ir.ui.menu')]).mapped('res_id')
            ir_view = self.env['ir.ui.menu'].sudo().search([('id', 'in', ir_model_data)])
            ir_view.write({'active': False})

    def update_silverdale_module(self):
        #fixme update functionality in next revision
        pass
        return True
        url = config.applist_url
        response = requests.get(url, json={}, timeout=30)
        response = response.json()
        IrParamSudo = self.env['ir.config_parameter'].sudo()
        expiry_date = IrParamSudo.get_param('sd_base_setup.sd_license_expire', False)
        if response.get('result', False) and response['result']['data'] and not expiry_date or expiry_date >= limit_date_str:
            apps = response['result']['data']
            ir_model_data = self.env['ir.model.data'].sudo().search([('module', '=', apps), ('model', '=', 'ir.ui.view')]).mapped('res_id')
            ir_view = self.env['ir.ui.view'].search([('active', '=', False),('id', 'in', ir_model_data)])
            ir_view.write({'active': True})
            ir_model_data = self.env['ir.model.data'].search([('module', '=', apps), ('model', '=', 'ir.ui.menu')]).mapped('res_id')
            ir_view = self.env['ir.ui.menu'].sudo().search([('active', '=', False),('id', 'in', ir_model_data)])
            ir_view.write({'active': True})

            apps = response['result']['data']
            domain = [('author', '=', 'Silverdale'), ('state', 'in', ['installed', 'to upgrade', 'to remove'])]
            installed_app = self.env['ir.module.module'].sudo().search(domain)
            apps = list(set.intersection(set(apps), set(installed_app.mapped('name'))))
            silverdale_apps = self.env['ir.module.module'].sudo().search([('name', 'in', apps)])
            silverdale_apps.button_immediate_upgrade()
    