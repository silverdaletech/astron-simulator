odoo.define('sd_pos.LotLine', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class LotLine extends PosComponent {
        get highlight() {
            let lot_text = ''
            let lot_id = null
            if (this.props.selectedLot !== null){
                lot_text = this.props.selectedLot.text
                lot_id = this.props.selectedLot._id
            }
            debugger;
            return this.props.lot.text !== lot_text && this.props.lot._id !== lot_id ? '' : 'highlight';
        }
    }
    LotLine.template = 'LotLine';
    Registries.Component.add(LotLine);
    return LotLine;
});
