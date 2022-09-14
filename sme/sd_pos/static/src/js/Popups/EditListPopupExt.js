odoo.define('sd_pos.EditListPopupExt', function(require) {
    'use strict';

    const { useState } = owl.hooks;
    const Registries = require('point_of_sale.Registries');
    const { useAutoFocusToLast } = require('point_of_sale.custom_hooks');
    const { _lt } = require('@web/core/l10n/translation');
    const EditListPopup = require('point_of_sale.EditListPopup');
    var core = require('web.core');
    var utils = require('web.utils');

    const EditListPopupExt = (EditListPopup) =>
        class extends EditListPopup {
            constructor() {
                super(...arguments);
                this.state = useState({
                    array: this._initialize(this.props.array),
                    lots: this._initialize(this.props.lots),
                    selectedLot: null
                });
                this.lot_search_string = this._search_string;
            }

            get _search_string () {
                var lot_search_string = "";
                for (var lot in this.state.lots) {
                    lot_search_string += this._lot_search_string(this.state.lots[lot]);
                }
                return utils.unaccent(lot_search_string);
            }

            get lots() {
                let res;
                if (this.state.query && this.state.query.trim() !== '') {
                    res = this.search_lot(this.state.query.trim());
                } else {
                    res = this.lotsArray;
                }
                return res.sort(function (a, b) { return (a.text || '').localeCompare(b.text || '') });
            }

            /*
            Create an array of lots
            */
            get lotsArray() {
                var lots = []
                var lotsArr = this.state.lots
                if (lotsArr.length > 0){
                    for (var i=0; i < lotsArr.length; i++){
                        lots.push({'_id': lotsArr[i]._id, 'text': lotsArr[i].text});
                    }
                }
                return lots
            }

            clickLot(event) {
                let lot = event.detail.lot;
                let lot_text = ''
                let lot_id = null
                if (this.state.selectedLot !== null){
                    lot_text = this.state.selectedLot.text
                    lot_id = this.state.selectedLot.id
                }
                if (lot_text === lot.text && lot_id === lot.id) {
                    this.state.selectedLot = null;
                } else {
                    this.state.selectedLot = lot;
                }
            }

            getPayload() {
                if (this.state.array[0].text === ''){
                    let lot_text = ''
                    if (this.state.selectedLot !== null){
                        lot_text = this.state.selectedLot.text
                    }
                    return {
                        newArray: this.state.lots
                            .filter((item) => item.text.trim() !== '' && item.text === lot_text)
                            .map((item) => Object.assign({}, item)),
                    };
                } else {
                    return {
                        newArray: this.state.array
                            .filter((item) => item.text.trim() !== '')
                            .map((item) => Object.assign({}, item)),
                    };
                }
            }

            _lot_search_string(lot) {
                var str =  lot.text || '';
                str = '' + lot._id + ':' + str.replace(':', '').replace(/\n/g, ' ') + '\n';
                return str;
            }

            search_lot(query) {
                try {
                    query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                    query = query.replace(/ /g,'.+');
                    var re = RegExp("([0-9]+):.*?"+utils.unaccent(query),"gi");
                }catch(e){
                    return [];
                }
                var results = [];
                for(var i = 0; i < 100; i++){
                    var r = re.exec(this.lot_search_string);
                    if(r){
                        var id = Number(r[1]);
                        results.push(this.lotsArray.find(l => l._id === id));
                    }else{
                        break;
                    }
                }
                return results;
            }

            async updateLotList(event) {
                this.state.query = event.target.value;
                const lots = this.lots;
                if (event.code === 'Enter' && lots.length === 1) {
                    this.state.selectedLot = lots[0];
                    this.confirm()
                } else {
                    this.render();
                }
            }
        };

    EditListPopup.defaultProps.lots = [];

    Registries.Component.extend(EditListPopup, EditListPopupExt);
    return EditListPopup;
});
