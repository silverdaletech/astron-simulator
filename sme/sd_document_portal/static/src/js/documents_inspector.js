odoo.define('sd_document_portal.SDDocumentsInspector', function (require) {
"use strict";

var DocumentsInspector = require('documents.DocumentsInspector');

DocumentsInspector.include({
    /*
        *@override*
        Render the share_document field in the view
    */
    _renderFields: function () {
        this._super(...arguments);
        const options = {mode: 'edit'};
        const proms = [];
        if (this.records.length === 1) {
            // Silverdale Added this line for share_document and share_with_company
            proms.push(this._renderField('share_document', options));
            proms.push(this._renderField('share_with_company', options));
        }
        return Promise.all(proms);
    },

    /*
        *@override*
        On share_document change trigger the share_ids method
        but pass no_popup key to restrict the popup for link share.
    */
    _onFieldChanged: async function (ev) {
        this._super(...arguments);
        if (ev.target.name === 'share_document'){
            if (ev.target.$el[0].children[0].checked === true){
                this.trigger_up('share_ids', {
                    resIds: this.records.map(record => record.res_id),
                    no_popup: true
                });
            }
            else{
                const result = await this._rpc({
                    model: 'documents.share',
                    method: 'unlink_live_shared_link',
                    args: [this.records.map(record => record.res_id)],
                });
            }
        }

        // Trigger change_folder_in_shared_links method via RPC call with new folder id
        if (ev.target.name === 'folder_id'){
            debugger;
            const result = await this._rpc({
                model: 'documents.document',
                method: 'change_folder_in_shared_links',
                args: [this.records.map(record => record.res_id), {'folder_id': ev.target.lastSetValue.id}],
            });
        }
    },

});

});
