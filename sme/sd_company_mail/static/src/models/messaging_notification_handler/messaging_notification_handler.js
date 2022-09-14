/** @odoo-module **/

import {
    registerInstancePatchModel,
    registerFieldPatchModel,
} from '@mail/model/model_core';
import { decrement, increment, insert, insertAndReplace, link, replace, unlink } from '@mail/model/model_field_command';

registerInstancePatchModel('mail.messaging_notification_handler', 'sd_company_mail/static/src/models/messaging_notification_handler/messaging_notification_handler.js', {
    /**
        SILVERDALE:: **Override**
        Get company from notification record via RPC and based on response notify user
    */
    async _handleNotificationNeedaction(data) {
        const response = await this.env.services.rpc({
            model: 'mail.message',
            method: 'get_company',
            args: [[data.id]]
        });
        if (response === false || response === Number(document.cookie.split('cids=')[1])) {
            const message = this.messaging.models['mail.message'].insert(
                this.messaging.models['mail.message'].convertData(data)
            );
            this.messaging.inbox.update({ counter: increment() });
            const originThread = message.originThread;
            if (originThread && message.isNeedaction) {
                originThread.update({ message_needaction_counter: increment() });
            }
        }
    },

});




