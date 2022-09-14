odoo.define('sd_document.DocumentsInspectorExt', function (require) {
    "use strict";

    var DocumentsInspector = require('documents.DocumentsInspector');
    const { _t, qweb } = require('web.core');
    const fieldRegistry = require('web.field_registry');
    const DocumentsViewMixin = require('documents.viewMixin');

    DocumentsInspector.include({
        /*
            *@override*
            add attach onclick event
        */
        events: _.extend({}, DocumentsInspector.prototype.events, {
            'click .o_inspector_attach': '_onAttachFile',
        }),

        /*
            *@override*
            Render the model_id field and record_id in the view
        */
        _renderFields: async function () {
            this._super(this, arguments)
            const options = {mode: 'edit'};
            const proms = [];
            if (this.records.length > 0) {
                proms.push(this._renderField('model_id', options));
                if (this.records[0].data.model_id) {
                    proms.push(this._renderField('model_record_id', options));
                }
            }
            return Promise.all(proms);
        },

        /*
            *@override*
            attach selected document with record
        */
        _onAttachFile: async function () {
            const record_ids = this.records.map(record => record.res_id)
            const record = this.records[0];
            if (record.data.model_id && record.data.model_record_id && record.data.model_record_id > 0) {
                const result = await this._rpc({
                    model: 'documents.document',
                    method: 'attach_file_with_record',
                    args: [record_ids, record.data.model_id.res_id, record.data.model_record_id],
                });
                if (result) {
                    this.trigger_up('open_record', {
                        resId: record.data.model_record_id,
                        resModel: result,
                    });
                }
            }
        },
    });

});






