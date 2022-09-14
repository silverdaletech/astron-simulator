odoo.define('sd_document_portal.viewMixinSD', function (require) {
'use strict';

const DocumentsViewMixin = require('documents.viewMixin');

/*
    *Patch*
    Add share_document and share_with_company in inspectorFields
*/

DocumentsViewMixin.inspectorFields.push('share_document');
DocumentsViewMixin.inspectorFields.push('share_with_company');
return DocumentsViewMixin;
});
