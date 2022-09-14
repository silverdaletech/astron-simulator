/** @odoo-module **/

import { SwitchCompanyMenu } from "@web/webclient/switch_company_menu/switch_company_menu";
import session from 'web.session';
import { patch } from "@web/core/utils/patch";
const { Component, hooks } = owl;
const { useState } = hooks;

patch(SwitchCompanyMenu.prototype, "sd_restrict_multicompany_checkboxes/static/src/webclient/switch_company_menu/switch_company_menu_ext.js", {

    async setup() {
        await this._super(...arguments);
        this.state.checkAccessToCheckBoxes = await session.user_has_group('sd_restrict_multicompany_checkboxes.group_can_access_company_checkboxes');
    },

});
