# -*- coding: utf-8 -*-
# from odoo import http


# class SdPosSquarePaymantTerminal(http.Controller):
#     @http.route('/sd_pos_square_paymant_terminal/sd_pos_square_paymant_terminal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sd_pos_square_paymant_terminal/sd_pos_square_paymant_terminal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sd_pos_square_paymant_terminal.listing', {
#             'root': '/sd_pos_square_paymant_terminal/sd_pos_square_paymant_terminal',
#             'objects': http.request.env['sd_pos_square_paymant_terminal.sd_pos_square_paymant_terminal'].search([]),
#         })

#     @http.route('/sd_pos_square_paymant_terminal/sd_pos_square_paymant_terminal/objects/<model("sd_pos_square_paymant_terminal.sd_pos_square_paymant_terminal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sd_pos_square_paymant_terminal.object', {
#             'object': obj
#         })
