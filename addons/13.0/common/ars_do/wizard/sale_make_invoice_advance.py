# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging as log


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        result = super().create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for sale_order in sale_orders:
            healthcare_card = sale_order.partner_id\
                                        .healthcare_cards\
                                        .filtered(lambda self: self.default_card == True)
            invoices = sale_order.mapped('invoice_ids')
            for invoice in invoices:
                if sale_order.healthcare_invoice == 'healthcare_invoice':
                    log.info('[Ars Do] Invoice: {} - {}'.format(invoice.id, invoice.name))
                    invoice.write({
                        'healthcare_invoice': sale_order.healthcare_invoice,
                        'healthcare_card': healthcare_card.id,
                        'created_from_sale': True
                    })

                    # for line in invoice.invoice_line_ids:
                    #     line.write({
                    #         'coverage': healthcare_card.healthcare_plan.default_coverage
                    #     })

                    #     line.update(line._get_price_total_and_subtotal())
                    #     line.update(line._get_fields_onchange_subtotal())
                elif sale_order.healthcare_invoice == 'not_healthcare_invoice':
                    invoice.write({
                        'healthcare_invoice': sale_order.healthcare_invoice,
                        'created_from_sale': True
                    })

        return result