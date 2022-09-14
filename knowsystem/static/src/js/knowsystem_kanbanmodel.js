/** @odoo-module **/

import KanbanModel from "web.KanbanModel";

const KnowSystemKanbanModel = KanbanModel.extend({
    /**
    * Re-write to explicitly retrieve searchDomain from element, when no options.domain is received
    */
    reload: function (id, options) {
        options = options || {};
        var element = this.localData[id];
        var searchDomain = options.domain || element.searchDomain || [];
        element.searchDomain = options.searchDomain = searchDomain;
        if (options.knowSystemDomain !== undefined) {
            options.domain = searchDomain.concat(options.knowSystemDomain);
        };
        return this._super.apply(this, arguments)
    },
});

export default KnowSystemKanbanModel;
