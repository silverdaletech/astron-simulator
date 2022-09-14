# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json 
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _send_confirmation_email(self):
        res =  super(StockPicking, self)._send_confirmation_email()
        company = self.env.company
        
        if not (company and company.invoice_on_delivery):
            return res
        
        so = self.sale_id
        if so and self.picking_type_code == 'outgoing':
            # for line in so.order_line:
            #     line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
            # invoice = so._create_invoices()
            invoice = False
            if any(so.order_line.mapped('qty_to_invoice')):
                invoice = so._create_invoices()
            
            if invoice:
                invoice.post()
                mail_template = company.delivery_invoice_email_template_id
                if not mail_template:
                    mail_template = self.env.ref('account.email_template_edi_invoice')

                lang = self.env.context.get('lang')
                if mail_template.lang:
                    lang = mail_template._render_lang(invoice.ids)[invoice.id]
                mail_template.with_context(lang=lang).send_mail(invoice.id, notif_layout="mail.mail_notification_light", force_send=True)

                selected_item = ''
                selected_item += invoice.name or "" + ","
                invoice_outstanding_details = json.loads(invoice.invoice_outstanding_credits_debits_widget)
                
                if invoice_outstanding_details and company.delivery_invoice_auto_reconcile:
                    lines = invoice_outstanding_details.get('content', False)
                    for line in lines:
                        line_id = line.get('id', False)
                        move = self.env['account.move'].browse(line.get('move_id'))
                        recon_line = self.env['account.move.line'].browse(line_id)
                        if not recon_line.reconciled:
                            invoice.js_assign_outstanding_line(line_id)

        return res