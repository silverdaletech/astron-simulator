/** @odoo-module **/

import {ProjectFormView} from "@project/js/project_form";
ProjectFormView.prototype.config.Controller.include({
    _onDomUpdated() {
        const $editable = this.$el.find('.note-editable');
        if ($editable.length) {
            const resizerHeight = this.$el.find('.o_wysiwyg_resizer').outerHeight();
            const newHeight = window.innerHeight - $editable.offset().top - resizerHeight + 300;
            $editable.outerHeight(550);
        }
    },
});