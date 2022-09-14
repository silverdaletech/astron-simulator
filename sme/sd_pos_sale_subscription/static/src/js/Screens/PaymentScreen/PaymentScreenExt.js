odoo.define('sd_pos_sale_subscription.PaymentScreenExt', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const PaymentScreenExt = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {

                /**
                    * @override

                    * Check is pos subscription is allowed for this pos instance,
                    * if yes, then set subscription_product_exists

                */

                super(...arguments);
                if (this.env.pos.config.allow_pos_subscriptions){
                    this.subscription_product_exists = this.checkSubscriptionProduct;
                }
            }

            get checkSubscriptionProduct () {
                const currentOrder = this.currentOrder;
                var sub_exists = false
                if (currentOrder.orderlines){
                    sub_exists = currentOrder.orderlines.any(line => line.get_product().recurring_invoice === true);
                    if (sub_exists){
                        sub_exists = true
                        this.currentOrder.set_to_invoice(true);
                    }else{
                        this.currentOrder.set_to_invoice(false);
                    }
                }
                return sub_exists
            }

            async toggleIsToInvoice() {
            /**
                * @override

                * Check is pos subscription is allowed for this pos instance,
                * if yes, then do not allow to toggle the is_to_invoice button, instead open an info popup

            */

                if (this.env.pos.config.allow_pos_subscriptions){
                    if (this.subscription_product_exists){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Invoice Required'),
                            body: this.env._t(
                                'Invoice is required for subscription products.'
                            ),
                        });
                        if (confirmed) {
                            this.render();
                        }
                    }else{
                        this.currentOrder.set_to_invoice(!this.currentOrder.is_to_invoice());
                    }
                    this.render();
                } else {
                    this.currentOrder.set_to_invoice(!this.currentOrder.is_to_invoice());
                    this.render();
                }

            }
        };

    Registries.Component.extend(PaymentScreen, PaymentScreenExt);

    return PaymentScreen;
});
