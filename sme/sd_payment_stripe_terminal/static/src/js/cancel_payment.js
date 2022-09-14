/* global AdyenCheckout */
odoo.define('sd_payment_stripe_terminal.cancel_payment', require => {
    'use strict';
//    console.log('*****************loading****************')
//
//    const core = require('web.core');
//    const checkoutForm = require('payment.checkout_form');
//    const manageForm = require('payment.manage_form');
//
//    const _t = core._t;
//
//    const STMixin = {
//
//
//
//        _dropinOnAdditionalDetails: function (state, dropin) {
//        debugger;
//            return this._rpc({
//                route: '/payment/adyen/payment_details',
//                params: {
//                    'acquirer_id': dropin.acquirerId,
//                    'reference': this.adyenDropin.reference,
//                    'payment_details': state.data,
//                },
//            }).then(paymentDetails => {
//                if (paymentDetails.action) { // Additional action required from the shopper
//                    dropin.handleAction(paymentDetails.action);
//                } else { // The payment reached a final state, redirect to the status page
//                    window.location = '/payment/status';
//                }
//            }).guardedCatch((error) => {
//                error.event.preventDefault();
//                this._displayError(
//                    _t("Server Error"),
//                    _t("We are not able to process your payment."),
//                    error.message.data.message
//                );
//            });
//        },
//
//        _dropinOnError: function (error) {
//        debugger;
//            this._displayError(
//                _t("Incorrect Payment Details"),
//                _t("Please verify your payment details.")
//            );
//        },
//
//        async _processPayment(provider, paymentOptionId, flow) {
//        debugger;
//            if (provider !== 'stripe_terminal' || flow === 'token') {
//                return this._super(...arguments); // Tokens are handled by the generic flow
//            }
//            if (this.adyenDropin === undefined) { // The drop-in has not been properly instantiated
//                this._displayError(
//                    _t("Server Error"), _t("We are not able to process your payment.")
//                );
//            } else {
//                return await this.adyenDropin.submit();
//            }
//        },
//
//    };
//
//    checkoutForm.include(STMixin);
//    manageForm.include(STMixin);
});













