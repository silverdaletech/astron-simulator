odoo.define('sd_pos_stripe_payment_terminal.models', function (require) {
var models = require('point_of_sale.models');
var Paymentsd_pos_stripe_payment_terminal = require('sd_pos_stripe_payment_terminal.payment');

models.register_payment_method('sd_pos_stripe_payment_terminal', Paymentsd_pos_stripe_payment_terminal);
models.load_fields('pos.payment.method', ['pos_stripe_api_key','registration_code','location_id','device_name','is_simulated_reader']);
});
