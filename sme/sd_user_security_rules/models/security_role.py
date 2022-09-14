# -*- coding: utf-8 -*-

import itertools

from itertools import chain, repeat
from collections import defaultdict

from odoo import api, models, fields

from odoo.addons.base.models.res_users import name_boolean_group, name_selection_groups, is_boolean_group, \
     is_selection_groups, is_reified_group, get_boolean_group, get_selection_groups, parse_m2m
from odoo.tools import partition


class security_role(models.Model):
    """
    The model to keep security rights combined in a role
    """
    _name = "security.role"
    _description = "User Role"

    def _default_group_ids(self):
        """
        Default method for group_ids: taken from default user
        """
        default_user_id = self.env['ir.model.data']._xmlid_to_res_id('base.default_user', raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().groups_id if default_user_id else []

    def _inverse_group_ids(self):
        """
        Inverse method for group_ids
        """
        for role in self:
            role.user_ids._inverse_security_role_ids()

    name = fields.Char(
        string="Name",
        required=True,
    )
    group_ids = fields.Many2many(
        "res.groups",
        "res_groups_security_role_rel_table",
        "res_group_id",
        "security_role_id",
        string="Security groups",
        default=_default_group_ids,
        inverse=_inverse_group_ids,
    )
    user_ids = fields.Many2many(
        "res.users",
        "security_role_res_users_rel_table",
        "res_users_id",
        "security_role_id",
        string="Users",
        inverse=_inverse_group_ids,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    color = fields.Integer(
        string='Color index',
        default=10,
    )

    @api.model
    def create(self, values):
        """
        Re-write to process dummy groups fields

        Methods:
         * _remove_reified_groups
        """
        values = self._remove_reified_groups(values)
        role = super(security_role, self).create(values)
        return role

    def write(self, values):
        """
        Re-write to process dummy groups fields

        Methods:
         * _remove_reified_groups
        """
        values = self._remove_reified_groups(values)
        res = super(security_role, self).write(values)
        return res

    def read(self, fields=None, load='_classic_read'):
        """
        Re-write to process dummy groups fields
         1. determine required group fields
         2. read regular fields and add group_ids if necessary
         3. add reified group fields

        Methods:
         * fields_get
         * is_reified_group
         * super of read
         * _add_reified_groups
        """
        # 1
        fields1 = fields or list(self.fields_get())
        group_fields, other_fields = partition(is_reified_group, fields1)
        # 2
        drop_group_ids = False
        if group_fields and fields:
            if 'group_ids' not in other_fields:
                other_fields.append('group_ids')
                drop_group_ids = True
        else:
            other_fields = fields
        res = super(security_role, self).read(other_fields, load=load)
        # 3
        if group_fields:
            for values in res:
                self._add_reified_groups(group_fields, values)
                if drop_group_ids:
                    values.pop('group_ids', None)
        return res

    @api.model
    def default_get(self, fields):
        """
        Re-write

        Methods:
         * is_reified_group
         * super of default_get
         * _add_reified_groups
        """
        group_fields, fields = partition(is_reified_group, fields)
        fields1 = (fields + ['group_ids']) if group_fields else fields
        values = super(security_role, self).default_get(fields1)
        self._add_reified_groups(group_fields, values)
        return values

    def onchange(self, values, field_name, field_onchange):
        """
        Re-write

        Methods:
         * is_reified_group
         * super
         * _add_reified_groups
        """
        field_onchange['group_ids'] = ''
        result = super().onchange(values, field_name, field_onchange)
        if not field_name:
            self._add_reified_groups(
                filter(is_reified_group, field_onchange),
                result.setdefault('value', {})
            )
        return result

    def _remove_reified_groups(self, values):
        """
        The method to return values without reified group fields

        Args:
         * values - dict of values

        Methods:
         * is_boolean_group
         * get_boolean_group
         * is_selection_groups
         * get_selection_groups

        Returns:
         * dict of updated values
        """
        add, rem = [], []
        values1 = {}
        for key, val in values.items():
            if is_boolean_group(key):
                (add if val else rem).append(get_boolean_group(key))
            elif is_selection_groups(key):
                rem += get_selection_groups(key)
                if val:
                    add.append(val)
            else:
                values1[key] = val
        if 'group_ids' not in values and (add or rem):
            values1['group_ids'] = list(itertools.chain(
                zip(repeat(3), rem),
                zip(repeat(4), add)
            ))
        return values1

    def _add_reified_groups(self, fields, values):
        """
        The method to add reified group fields to values

        Args:
         * fields
         * values

        Methods:
         * parse_m2m
         * is_boolean_group
         * get_boolean_group
         * get_selection_groups
        """
        gids = set(parse_m2m(values.get('group_ids') or []))
        for f in fields:
            if is_boolean_group(f):
                values[f] = get_boolean_group(f) in gids
            elif is_selection_groups(f):
                selected = [gid for gid in get_selection_groups(f) if gid in gids]
                values[f] = selected and selected[-1] or False

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Re-write to get dummy group fields

        Method:
         * super of fields_get
         * get_groups_by_application
         * name_selection_groups
         * name_boolean_group
        """
        res = super(security_role, self).fields_get(allfields, attributes=attributes)
        Group = self.env['res.groups'].sudo()
        for app, kind, gs, category_name in Group.get_groups_by_application():
            if kind == 'selection':
                selection_vals = [(False, '')]
                if app.xml_id == 'base.module_category_user_type':
                    selection_vals = []
                gs_list = [gs]
                if app.xml_id == 'base.module_category_accounting_accounting':
                    ranks = defaultdict(list)
                    for g in gs:
                        ranks[len(g.trans_implied_ids & gs)].append(g)
                    perms = [
                        [Group.concat(*perm) for perm in itertools.permutations(rank)]
                        for k, rank in sorted(ranks.items())
                    ]
                    gs_list = [Group.concat(*perm) for perm in itertools.product(*perms)]
                for gs in gs_list:
                    field_name = name_selection_groups(gs.ids)
                    if allfields and field_name not in allfields:
                        continue
                    tips = ['%s: %s' % (g.name, g.comment) for g in gs if g.comment]
                    res[field_name] = {
                        'type': 'selection',
                        'string': app.name or _('Other'),
                        'selection': selection_vals + [(g.id, g.name) for g in gs],
                        'help': '\n'.join(tips),
                        'exportable': False,
                        'selectable': False,
                    }
            else:
                for g in gs:
                    field_name = name_boolean_group(g.id)
                    if allfields and field_name not in allfields:
                        continue
                    res[field_name] = {
                        'type': 'boolean',
                        'string': g.name,
                        'help': g.comment,
                        'exportable': False,
                        'selectable': False,
                    }
        return res

    def action_create_user(self):
        """
        The method to open a user form view with pre-filled groups

        Returns:
         * ir.actions.window

        Extra info:
         * Expected singletom
        """
        self.ensure_one()
        action = self.sudo().env.ref("sd_user_security_rules.action_res_users_only_form").read()[0]
        action["context"] = {
            "default_groups_id": [(6, 0, self.group_ids.ids)],
            "default_security_role_ids": [(6, 0, self.ids)],
            "form_view_ref": "base.view_users_form",
        }
        return action
