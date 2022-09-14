/** @odoo-module **/

import core from 'web.core';
import ajax from 'web.ajax';
import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';

var SdActionMenu = Widget.extend({
    template: 'sd_status_menu',

    events: {
        'click .composerClicked': 'onClickFullComposer',
    },

    init: function (parent, options) {
        this._super(parent);
        this.sd_modules = 0;
        this.modules_installed = 0;
        this.modules_not_installed = 0;
        this.loaded = false;
    },

    willStart: function () {
        const modulesPromise = this._rpc({
            model: 'ir.module.module',
            method: 'get_silverdale_apps',
        })
        return Promise.all(
            [modulesPromise]
        ).then(this._loadedCallback.bind(this));
    },

    _loadedCallback: function ([modules]) {
        // Process modules count
        this.sd_modules = modules.sd_modules;
        this.modules_installed = modules.modules_installed;
        this.modules_not_installed = modules.modules_not_installed;
        this.loaded = true;
    },

    onClickFullComposer() {
        this.openFullComposer();
    },

    async openFullComposer() {
        var defaultData = await this._rpc({
                model: 'mail.compose.message',
                method: 'get_help_default_data',
                args: [],
            });
        const context = {
            default_partner_ids: [defaultData.recipient_id],
            default_is_for_help: true,
            default_template_id: defaultData.template_id,
        };

        const action = {
            name: ("Get Help"),
            type: 'ir.actions.act_window',
            res_model: 'mail.compose.message',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new',
            context: context,
        };

        debugger;
        this.trigger().do_action(action)

    }

});
SystrayMenu.Items.push(SdActionMenu);

export { SdActionMenu };
