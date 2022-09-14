odoo.define('sd_pos.ClosePosPopupExt', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');
    const { identifyError } = require('point_of_sale.utils');
    const { ConnectionLostError, ConnectionAbortedError} = require('@web/core/network/rpc_service');
    const { nextFrame } = require('point_of_sale.utils');

    const ClosePosPopupExt = (ClosePosPopup) =>
        class extends ClosePosPopup {

            getVisibility() {
                var visibility = 'hidden'
                if (this.env.pos.config.print_closing_stats && !this.env.pos.config.auto_print_closing_stats){
                    visibility = 'visible'
                }
                return "visibility: " + visibility + ";";
            }

            async _printPosClosing(canvas) {
                var imageDatas =  canvas.toDataURL('image/png');
                const newWindow = window.open("about:blank", "", "menubar=no, width=800, height=800");;
                newWindow.document.write(
                    `<html>
                        <head>
                            <script>
                                function onloadImage() {
                                    setTimeout('printImage()', 10);
                                }
                                function printImage() {
                                    window.print();
                                    window.close();
                                }
                            </script>
                            <title>POS Closing (${new Date().toLocaleString()})</title>
                        </head>
                        <body onload='onloadImage()'>
                            <img src='${imageDatas}'></img>
                        </body>
                    </html>`
                );
                newWindow.document.close();
            }

            async htmlToImg(closingDataEl) {
                self = this
                var promise = new Promise(function (resolve, reject) {
                    closingDataEl = $('.modal-dialog>.close-pos-popup');
                    html2canvas(closingDataEl[0], {
                        onrendered: function (canvas) {
                            resolve(self._printPosClosing(canvas));
                        },
                    })
                });
                return true;
            }

            async printClosingStats(){
                const closingDataEl = $(".close-pos-popup")
                this.htmlToImg(closingDataEl[0].outerHTML);
                return true
            }

            async closeSession() {
                if (this.canCloseSession() && !this.closeSessionClicked) {
                    if (this.env.pos.config.print_closing_stats && this.env.pos.config.auto_print_closing_stats){
                        await this.printClosingStats()
                        return super.closeSession();
                    } else {
                        return super.closeSession();
                    }
                }
            }
        };
    Registries.Component.extend(ClosePosPopup, ClosePosPopupExt);
    return ClosePosPopup;
});