/** @odoo-module **/

import {registerInstancePatchModel} from '@mail/model/model_core';
import { clear } from '@mail/model/model_field_command';

registerInstancePatchModel('mail.chatter', 'sd_mail_compose.chatter.js', {
    onClickSendMessage(ev) {
        this._super.apply(this, arguments);
        if (this.composerView && !this.composerView.composer.isLog) {
            this.composerView.openFullComposer();
            this.update({ composerView: clear() });
        };
    },
});


 