/** @odoo-module **/
import { registerFieldPatchModel, registerClassPatchModel} from '@mail/model/model_core';

import { attr } from '@mail/model/model_field';

registerFieldPatchModel('mail.message', 'sd_bcc_mail/static/src/js/message_inherit.js', {
    email_bcc: attr({ default: false }),
});

registerClassPatchModel('mail.message', 'sd_bcc_mail/static/src/js/message_inherit.js', {
        /**
         * @override
         */
        convertData(data) {
            const res = this._super(data);
            if ('email_bcc' in data) {
                res.email_bcc = data.email_bcc;
            }
            return res;
        },
    });

