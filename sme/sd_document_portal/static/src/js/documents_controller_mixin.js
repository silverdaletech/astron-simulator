odoo.define("sd_document_portal.DocumentsKanbanControllerSD", function (require) {
    "use strict";

    const config = require('web.config');
    const DocumentsKanbanController = require("documents.DocumentsKanbanController");

    const DocumentsKanbanControllerSD = {

        async _shareDocuments(vals) {
            if (!vals.folder_id) {
                return;
            }
            const result = await this._rpc({
                model: 'documents.share',
                method: 'open_share_popup',
                args: [vals],
            });
            if (result === false){
                return true
            }
            else{
                this.do_action(result, {
                    fullscreen: config.device.isMobile,
                });
            }
        },

        _onShareIds(ev) {
        debugger;
            ev.stopPropagation();
            this._shareDocuments({
                document_ids: [[6, 0, ev.data.resIds]],
                folder_id: this.searchModel.get('selectedFolderId'),
                type: 'ids',
                no_popup: ev.data.no_popup,
                doc_ids: ev.data.resIds
            });
        },
    };

    DocumentsKanbanController.include(DocumentsKanbanControllerSD);

});

