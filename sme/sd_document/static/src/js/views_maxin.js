odoo.define('sd_document.views_maxin', function (require) {
'use strict';

const DocumentsViewMixin = require('documents.viewMixin');

/*
    *Patch*
    Add share_document in inspectorFields
*/

DocumentsViewMixin.inspectorFields.push('model_id');
DocumentsViewMixin.inspectorFields.push('model_record_id');
return DocumentsViewMixin;
});




