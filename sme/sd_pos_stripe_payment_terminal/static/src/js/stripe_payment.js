odoo.define("sd_pos_stripe_payment_terminal.payment", function (require) {
  "use strict";

  var core = require("web.core");
  var rpc = require("web.rpc");
  var terminal;
  var simulate_card_response;
  var PaymentInterface = require("point_of_sale.PaymentInterface");
  const { Gui } = require("point_of_sale.Gui");
  var ajax = require("web.ajax");
  var is_simulated_reader = "";
  var payment_id;
  var payment_method_id = null;
  var is_connected = false;

  var _t = core._t;

  function capturePayment(payment_id,pay_status,st_interac_present) {
    // Your backend should call /v1/terminal/connection_tokens and return the JSON response from Stripe
    debugger;
    return ajax
      .jsonRpc("/pos_capture_payment", "call", {
        payment_id: payment_id,
        payment_method_id: payment_method_id,
        payment_status : pay_status,
        st_interac_present : st_interac_present
      })
      .then(function (response) {
        return response;
      });
  }

  function unexpectedDisconnect() {
    //    don't remove this fucntion. it is using to call stripe sdk
  }

  function connectReaderHandler(is_test, location_id) {
    if (is_test) {
      // for simulator reader
      var config = { simulated: true };
    } else {
      // for card reader

      var config = { simulated: false, location: location_id };
    }

    var data;
    return terminal.discoverReaders(config).then(function (discoverResult) {
      if (discoverResult.error) {
        console.log("Failed to discover: ", discoverResult.error);
        data = {
          error: true,
          message: discoverResult.error.message,
        };
        return data;
      } else if (discoverResult.discoveredReaders.length === 0) {
        console.log("No available readers. Please check your reader is registered with your stripe location or not!");
        data = {
          error: true,
          message: "No available readers. Please check your reader is registered with your stripe location or not!",
        };
        return data;
      } else {
        // Just select the first reader here.
        var selectedReader = discoverResult.discoveredReaders[0];

        return terminal
          .connectReader(selectedReader, { fail_if_in_use: true })
          .then(function (connectResult) {
            if (connectResult.error) {
              console.log("Failed to connect: ", connectResult.error);
              var data = {
                error: true,
                message: connectResult.error.message,
              };
              return data;
            } else {
              console.log("Connected to reader: ", connectResult.reader.label);
              var data = {
                error: false,
                message: connectResult.reader.label,
              };
              return data;

              //
            }
          });
      }
    });
  }

  var StripePaymentTerminal = PaymentInterface.extend({

    send_payment_request: function (cid) {
      this.was_cancelled = false;
      is_connected = false;
      self = this;
      var line = this.pos.get_order().selected_paymentline;
      payment_method_id = line.payment_method.id;
      this._super.apply(this, arguments);
      return rpc
        .query({
          model: "pos.payment.method",
          method: "pos_credential_test",
          args: [line.payment_method.id],
        })
        .then(function (result) {
          if (result == "invalid_key") {
            //            self.unexpectedDisconnect();
            debugger;
            simulate_card_response = false;
            self._show_error(
              _t("Authentication failed. Please check your Stripe credentials.")
            );
            line.set_payment_status("retry");
            return Promise.resolve();
          } else {
            return self._sd_pos_stripe_payment_terminal_pay();
          }
        });
    },
    send_payment_cancel: function (order, cid) {
     debugger;
      clearInterval(this.polling);
      this._super.apply(this, arguments);
      this.was_cancelled = true;
      if (is_connected) {
        this._sd_pos_stripe_payment_terminal_cancel();
      }

      return Promise.resolve();
    },

    close: function ()
     {
      this._super.apply(this, arguments);
    },

    // private methods
    _reset_state: function () {
      this.was_cancelled = false;
      this.last_diagnosis_service_id = false;
      this.remaining_polls = 4;
      clearTimeout(this.polling);
    },

    // Stripe terminal refund
    _sd_stripe_payment_terminal_refund: function(data,line){
        // refund from stripe payment terminal
           debugger;
         return ajax
            .jsonRpc("/pos_refund_payment", "call", {
                orderId: data.refunded_orderline_id,
                payment_method_id: payment_method_id,
                amount: line.amount


            })
            .then(function(response) {
            debugger;
            if (response.error==false){
            console.log('refunded data : ',response.data)
            Promise.resolve();
            return response
            }
            else
            {
            self._show_error(_t("Error while return amount  from stripe : "+response.data));
             line.set_payment_status("retry");
             Promise.reject()
             return response

            }



            });



        },

    _handle_odoo_connection_failure: function (data) {
      // handle timeout

      console.log("Handlingggggggggggggggggggggg", data);
      var line = this.pos.get_order().selected_paymentline;
      debugger;
      if (data.error && data.error.code == "canceled") {
        if (line) {
          line.set_payment_status("retry");
        }

        this._show_error(_t("Stripe Transaction Cancelled."));
      } else {
        if (line) {
          line.set_payment_status("retry");
        }

        this._show_error(
          _t(
            "Could not connect to the Odoo server, please check your internet connection and try again."
          )
        );
      }

      // prevent subsequent onFullFilled's from being called
    },

    paymentIntent: function () {
      var line = this.pos.get_order().selected_paymentline;
      var real_amount = line.amount;
      var currency = this.pos.currency.name;

      if (line.payment_method.is_simulated_reader) {
        real_amount = parseInt(real_amount * 100);
      } else {
        real_amount = real_amount * 100;
      }

      console.log("calling payment intent...");
      return ajax
        .jsonRpc("/pos_payment_intent", "call", {
          amount: real_amount,
          payment_method_id: payment_method_id,
          currency: currency,
        })
        .then(function (response) {
          return response;
        })
        .then(function (data) {
          if (data.error) {
            self._show_error(
              _t("Sorry! Could not Intent Payment. " + data.error)
            );
            console.log("Sorry! Could not Intent Payment. " + data.error);
            var line = self.pos.get_order().selected_paymentline;
            line.set_payment_status("retry");
            return Promise.reject();
            //              return data;
          } else {
            var clientSecret = data.client_secret;
            return clientSecret.toString();
          }
        });
    },

    connection_stripe: function (data, operation) {
      return ajax
        .jsonRpc("/pos_connection_token", "call", {
          payment_method_id: payment_method_id,
        })
        .then(function (response) {
          return JSON.parse(response);
        })
        .then(function (data) {
          if (data.error) {
            return data;
          } else return data.secret;
        });
    },

    _sd_pos_stripe_payment_terminal_get_sale_id: function () {
      var config = this.pos.config;
      return _.str.sprintf("%s (ID: %s)", config.display_name, config.id);
    },

    _sd_pos_stripe_payment_terminal_common_message_header: function () {
      var config = this.pos.config;
      this.most_recent_service_id = Math.floor(
        Math.random() * Math.pow(2, 64)
      ).toString(); // random ID to identify request/response pairs
      this.most_recent_service_id = this.most_recent_service_id.substring(
        0,
        10
      ); // max length is 10

      return {
        ProtocolVersion: "3.0",
        MessageClass: "Service",
        MessageType: "Request",
        SaleID: this._sd_pos_stripe_payment_terminal_get_sale_id(config),
        ServiceID: this.most_recent_service_id,
        POIID:
          this.payment_method
            .sd_pos_stripe_payment_terminal_terminal_identifier,
      };
    },

    _sd_pos_stripe_payment_terminal_pay_data: function () {
      var order = this.pos.get_order();
      var config = this.pos.config;
      var line = order.selected_paymentline;
      var data = {
        SaleToPOIRequest: {
          MessageHeader: _.extend(
            this._sd_pos_stripe_payment_terminal_common_message_header(),
            {
              MessageCategory: "Payment",
            }
          ),
          PaymentRequest: {
            SaleData: {
              SaleTransactionID: {
                TransactionID: order.uid,
                TimeStamp: moment().format(), // iso format: '2018-01-10T11:30:15+00:00'
              },
            },
            PaymentTransaction: {
              AmountsReq: {
                Currency: this.pos.currency.name,
                RequestedAmount: line.amount,
              },
            },
          },
        },
      };

      if (config.sd_pos_stripe_payment_terminal_ask_customer_for_tip) {
        data.SaleToPOIRequest.PaymentRequest.SaleData.SaleToAcquirerData =
          "tenderOption=AskGratuity";
      }

      return data;
    },

    _sd_pos_stripe_payment_terminal_pay: function () {
      var self = this;
      var line = this.pos.get_order().selected_paymentline;
      var order = this.pos.get_order();
      if (!line) {
        return Promise.reject();
      }
      if (this.was_cancelled) {
        return Promise.resolve();
      }

        // refund from stripe
        debugger;
         if (order.selected_paymentline.amount < 0 && line.order.selected_orderline.refunded_orderline_id) {
            debugger;
              return this.connection_stripe().then(function(data) {
              debugger
                return self._sd_stripe_payment_terminal_refund(line.order.selected_orderline,line).then(function(refund_res){
                debugger
                if (!refund_res.error)
                {
                order.selected_paymentline.refunded_id = refund_res.id
                return true
                }
                else
                {
                  line.set_payment_status("retry");
//                    Promise.reject()
                    return false
                }

                });
            });


            }

         if (order.selected_paymentline.amount < 0) {
                this._show_error(
                    _t("Cannot process transactions with negative amount.")
                );
                return Promise.resolve();
            }


      if (order === this.poll_error_order) {
        delete this.poll_error_order;
        return self._sd_pos_stripe_payment_terminal_handle_response({});
      }

      var data = this._sd_pos_stripe_payment_terminal_pay_data();
      line.set_payment_status("waiting");
      return this.connection_stripe().then(function (data) {
        return self._sd_pos_stripe_payment_terminal_handle_response(data);
      });
    },

    _sd_pos_stripe_payment_terminal_cancel: function (ignore_error) {
      var self = this;
      var data = "";
      var line = this.pos.get_order().selected_paymentline;

      debugger;
      if (terminal) {
        terminal.cancelCollectPaymentMethod().then(function (config) {
          if (config) {
            debugger;
            console.log("Successfully Cancelled the payment. ", config);
            //            return Promise.resolve()
          } else {
            console.log("Failed to Cancel the payment. ");
          }
        });
      }
    },

    _convert_receipt_info: function (output_text) {
      return output_text.reduce(function (acc, entry) {
        var params = new URLSearchParams(entry.Text);

        if (params.get("name") && !params.get("value")) {
          return acc + _.str.sprintf("<br/>%s", params.get("name"));
        } else if (params.get("name") && params.get("value")) {
          return (
            acc +
            _.str.sprintf(
              "<br/>%s: %s",
              params.get("name"),
              params.get("value")
            )
          );
        }

        return acc;
      }, "");
    },

    _poll_for_response: function (resolve, reject) {
      var line = this.pos.get_order().selected_paymentline;
      if (!line) {
        return Promise.reject();
      }

      var self = this;
      if (this.was_cancelled) {
        resolve(false);
        return Promise.resolve();
      }

      if (terminal) {
        if (line.payment_method.is_simulated_reader) {
          terminal.setSimulatorConfiguration({
            testCardNumber: "4242424242424242",
          });
        }

        var payment_intent = self.paymentIntent();

        return payment_intent.then(function (data) {
          //            if there is error in response
          if (data.error) {
            debugger;
            if (self.remaining_polls != 0) {
              self.remaining_polls--;
              return Promise.reject();
              self._handle_odoo_connection_failure(data);
            } else {
              reject();
              self.poll_error_order = self.pos.get_order();
              return Promise.reject();
              self._handle_odoo_connection_failure(data);
            }
            resolve(false);
            return Promise.reject();
          } else {
            is_connected = true;
            var clientSecret = data;
            return terminal
              .collectPaymentMethod(clientSecret)
              .then(function (result) {
                if (result.error) {
                  // Placeholder for handling result.error
                  console.log("Error while initiating payment", result.error);
                  //                                    debugger;
                  if (self.remaining_polls != 0) {
                    self.remaining_polls--;
                    return self._handle_odoo_connection_failure(result);
                  } else {
                    //                                        debugger;
                    self.poll_error_order = self.pos.get_order();
                    return self._handle_odoo_connection_failure(result);
                  }
                  return Promise.reject();
                } else {
                  // Placeholder for processing result.paymentIntent

                  console.log(
                    "Successfully initiated payment",
                    result.paymentIntent
                  );

                  //  self.remaining_polls = 2;
                  return terminal
                    .processPayment(result.paymentIntent)
                    .then(function (result) {
                      if (result.error) {
                        console.log(
                          "Error while Process payment",
                          result.error
                        );
                        self._show_error(
                          _t(
                            "Error while Process payment. " +
                              result.error.message
                          )
                        );

                        // Placeholder for handling result.error

                        if (self.remaining_polls != 0) {
                          self.remaining_polls--;
                        } else {
                          self.poll_error_order = self.pos.get_order();
                        }
                        return Promise.reject();
                      } else if (result.paymentIntent) {
                        // Placeholder for notifying your backend to capture result.paymentIntent.id
                        console.log(
                          "Successfully  payment",
                          result.paymentIntent.id
                        );
                        return capturePayment(result.paymentIntent.id,
                        result.paymentIntent.status,
                        result.paymentIntent.charges.data[0].payment_method_details.type).then(
                          function (response) {
                            if (response.error) {
                              // revert the initiated payment
                              self._show_error(
                                _t(response.error.message)
                              );
                              line.set_payment_status("retry");
                              resolve(false);
                              //                                                                                                        return Promise.reject(response)
                            } else {
                                debugger
                                line.charge_id = result.paymentIntent.charges.data[0].id;
                                line.transaction_id = result.paymentIntent.id;
                                if (result.paymentIntent.charges.data[0].payment_method_details.type=='card_present'){
                                line.card_type =
                                        result.paymentIntent.charges.data[0].payment_method_details.card_present.brand;
                                    line.cardholder_name =
                                        result.paymentIntent.charges.data[0].payment_method_details.card_present.cardholder_name;

                                    line.last_digits = '*****' + result.paymentIntent.charges.data[0].payment_method_details.card_present.last4;
                                }
                                else if(result.paymentIntent.charges.data[0].payment_method_details.type == 'interac_present'){
                                line.card_type =
                                        result.paymentIntent.charges.data[0].payment_method_details.interac_present.brand;
                                    line.cardholder_name =
                                        result.paymentIntent.charges.data[0].payment_method_details.interac_present.cardholder_name;

                                    line.last_digits = '*****' + result.paymentIntent.charges.data[0].payment_method_details.interac_present.last4;

                                }


                              line.set_payment_status("done");
                              resolve(true);
                              self.last_diagnosis_service_id = true;
                              console.log(
                                " self.last_diagnosis_service_id ",
                                self.last_diagnosis_service_id
                              );
                            }
                          }
                        );
                      }
                    });
                }
              });
          }

          if (self.remaining_polls <= 0) {
            self._show_error(
              _t(
                "The connection to your payment terminal failed. Please check if it is still connected to the internet."
              )
            );
            self._sd_pos_stripe_payment_terminal_cancel();
            resolve(false);
          }
        });
      }
    },

    _sd_pos_stripe_payment_terminal_handle_response: function (response) {
      if (this.was_cancelled) {
        return Promise.resolve();
      }
      var line = this.pos.get_order().selected_paymentline;

      if (response.error) {
        this._show_error(
          _t("Authentication failed. Please check your Stripe credentials.")
        );
        line.set_payment_status("force_done");
        return Promise.resolve();
      } else {
        var self = this;

        var res = new Promise(function (resolve, reject) {
          // clear previous intervals just in case, otherwise
          // it'll run forever

          clearTimeout(self.polling);
          terminal = StripeTerminal.create({
            onFetchConnectionToken: self.connection_stripe,
            onUnexpectedReaderDisconnect: unexpectedDisconnect,
          });
          var is_test = false;
          var location_id;
          var device_name;
          var registration_code;
          if (line.payment_method.is_simulated_reader) {
            is_test = true;
          } else {
            location_id = line.payment_method.location_id;
            device_name = line.payment_method.device_name;
            registration_code = line.payment_method.registration_code;
          }

          simulate_card_response = connectReaderHandler(is_test, location_id);

          simulate_card_response.then(function (resp) {
            console.log("With Simulated card reader......", resp);
            if (self.was_cancelled) {
              resolve(false);
              return Promise.resolve();
              clearTimeout(self.polling);
            }
            self.polling = setInterval(function () {
              if (!response.error) {
                if (resp && !resp.error) {
                  line.set_payment_status("waitingCard");
                  var test = self._poll_for_response(resolve, reject);
                  if (self.last_diagnosis_service_id == true) {
                    clearTimeout(this.polling);
                  }
                  //                                    test.then(function(data) {
                  //                                        console.log('dataaa', data)
                  //                                    });

                  clearInterval(self.polling);
                  return test;
                } else {
                  line.set_payment_status("retry");

                  var message;
                  if (resp && resp.message) {
                    if (resp.message.message) {
                      message = resp.message.message;
                    } else {
                      message = resp.message;
                    }
                  } else {
                    message =
                      "Failed to connect to the reader. Please retry again!";
                  }

                  console.log("Message", message);
                  self._show_error(_t(message));

                  resolve(false);
                }
              }
            }, 5500);
          });
        });

        // make sure to stop polling when we're done
        res.finally(function () {
          self._reset_state();
        });

        return res;
      }
    },

    _show_error: function (msg, title) {
      clearInterval(this.polling);
      this.was_cancelled = true;
      if (!title) {
        title = _t("Stripe Terminal Error:");
      }
      Gui.showPopup("ErrorPopup", {
        title: title,
        body: msg,
      });
//      return Promise.reject();
    },
  });




  return StripePaymentTerminal;
});
