odoo.define('sd_widgets.AbstractField', function (require) {
"use strict";

var field_utils = require('web.field_utils');
var AbstractField = require('web.AbstractField');
var Widget = require('web.Widget');

AbstractField.include({

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * highlight the current field for kiosk numpad.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _onClick: function (ev) {
        if (ev.currentTarget.className.includes('js-kioskboard-input') === true){

            var parentElements = ev.currentTarget.parentElement.parentElement.parentElement;
            var allInputs = parentElements.querySelectorAll('input');
            var allLabels = parentElements.querySelectorAll('label');
            var currentElementLabel = ev.currentTarget.parentElement.parentElement.querySelector('label').attributes.for;
            var filteredLabels = [...allLabels].filter(l => l.attributes.for !== currentElementLabel);
            var filteredInputs = [...allInputs].filter(i => i.id !== ev.currentTarget.id);
            for (let i=0; i<filteredLabels.length; i++){
                filteredLabels[i].style.color = '#091124';
            }
            for (let j=0; j<filteredInputs.length; j++){
                filteredInputs[j].style.border = '1px solid #ccc';
                filteredInputs[j].style.borderWidth = '0 0 1px 0';
            }

            ev.currentTarget.parentElement.parentElement.querySelector('label').style.color = '#01666b'
            ev.currentTarget.style.border = '1px solid #01666b'
            ev.currentTarget.style.borderWidth = '0 0 1px 0'
        }
        this._super.apply(this, arguments);

    },

});


});
