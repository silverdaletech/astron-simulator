odoo.define('sd_pos_sale_subscription.ProductScreenExt', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const ProductScreenExt = (ProductScreen) =>
        class extends ProductScreen {

            async _onClickPay() {

            /**
                * @override

                * Check if pos subscription is allowed for this pos instance,
                * if yes, require customer if subscription product exists in order lines.
                * call super to resume normal flow

            */
                if (this.env.pos.config.allow_pos_subscriptions){
                    if (this.env.pos.get_order().orderlines.any(line => line.get_product().recurring_invoice === true) && this.currentOrder.get_client() == null){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Please select the Customer'),
                            body: this.env._t(
                                'Subscription Product found in order, you need to select the customer before you can proceed.'
                            ),
                        });
                        if (confirmed) {
                            this._onClickCustomer();
                        }
                    }
                }
                return super._onClickPay(...arguments);
            }
        };
    Registries.Component.extend(ProductScreen, ProductScreenExt);
    return ProductScreen;
});
