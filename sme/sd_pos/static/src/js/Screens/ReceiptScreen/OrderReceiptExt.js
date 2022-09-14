odoo.define("sd_pos.OrderReceiptExt", function (require) {
    "use strict";
    const Registries = require('point_of_sale.Registries');
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    /*
        Create an Logo url and address object for printing in receipt
    */
    const OrderReceiptExt = (OrderReceipt) =>
        class extends OrderReceipt {
            get posLogoUrl() {
                if (this.env.pos){
                    if (this.env.pos.config){
                        if(this.env.pos.config.has_pos_specific_info && this.env.pos.config.set_logo){
                            if (this.env.pos.config.logo !== false){
                                var url = '/web/image?model=pos.config&field=logo&id=' + this.env.pos.config_id;
                                return url
                            }else{
                                return false
                            }
                        }
                    }
                }
            }

            get pos_address() {
                if (this.env.pos){
                    if (this.env.pos.config){
                        if(this.env.pos.config.has_pos_specific_info && this.env.pos.config.set_address){
                            var receiptEnv = this.receiptEnv
                            var company = false
                            if (receiptEnv !== false){
                                var receipt = receiptEnv.receipt
                                if (receipt !== false){
                                    company = receipt.company
                                }
                            }
                            if (company !== false){
                                var vat_label = company.vat_label
                            }
                            return {
                                'phone': this.env.pos.config.phone,
                                'vat': this.env.pos.config.vat,
                                'vat_label': vat_label,
                                'email': this.env.pos.config.email,
                                'website': this.env.pos.config.website,
                            }
                        }else{
                            return false
                        }
                    }
                }
            }
        };
    Registries.Component.extend(OrderReceipt, OrderReceiptExt);
    return OrderReceipt;
});