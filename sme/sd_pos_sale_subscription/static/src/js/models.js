odoo.define("sd_pos_sale_subscription.models", function (require){
    "use strict";

    const models = require('point_of_sale.models');
    const _super_posmodel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
            // some new code in this method
            models.load_fields('product.product',['recurring_invoice']);
            _super_posmodel.initialize.apply(this, arguments);
        },
    });

});