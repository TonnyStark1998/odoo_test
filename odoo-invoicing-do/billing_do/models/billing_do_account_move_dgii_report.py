import logging
from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

class BillingDoAccountMoveDgiiReport(models.Model):
    _inherit = "account.move"

    report_vat = fields.Char(related='partner_id.vat', string='Tax Contributor ID', store=False)
    report_vat_type = fields.Char(compute='_compute_report_vat_type', string='Tax Contributor Type', store=False)
    report_reversed_move = fields.Char(related='reversal_move_id.name', string='Tax Receipt Reversed', store=False)
    report_invoice_date_month = fields.Char(string='Invoice Date Month', compute='_compute_report_invoice_date')
    report_invoice_date_day = fields.Char(string='Invoice Date Day', compute='_compute_report_invoice_date')
    report_payment_date_month = fields.Char(string='Payment Date Month', store=False)
    report_payment_date_day = fields.Char(string='Payment Date Day', store=False)
    report_service_amount = fields.Monetary(string='Service Amount', default=0.0, currency_field='company_currency_id', compute='_compute_service_consumable_amount')
    report_consumable_amount = fields.Monetary(string='Consumable Amount', default=0.0, currency_field='company_currency_id', compute='_compute_service_consumable_amount')
    report_total_amount = fields.Monetary(string='Total Amount', default=0.0, store=False)
    
    report_itbis_billed_amount = fields.Monetary(string='ITBIS Billed Amount', store=False)
    report_itbis_held_amount = fields.Monetary(string='ITBIS Held Amount', store=False)
    report_itbis_proportional_amount = fields.Monetary(string='ITBIS Proportional Amount', store=False)
    report_itbis_expense_amount = fields.Monetary(string='ITBIS Expense Amount', store=False)
    report_itbis_ahead_amount = fields.Monetary(string='ITBIS Ahead Amount', store=False)
    report_itbis_purchases_amount = fields.Monetary(string='ITBIS Purchases Amount', store=False)
    report_isr_type = fields.Char(string='ISR Type', store=False)
    report_isr_held_amount = fields.Monetary(string='ISR Held Amount', store=False)
    report_isr_purchases_amount = fields.Monetary(string='ISR Purchases Amount', store=False)
    report_isc_amount = fields.Monetary(string='ISC Amount', store=False)
    report_other_taxes_amount = fields.Monetary(string='Other Taxes Amount', store=False)
    report_legaltip_amount = fields.Monetary(string='Legal Tip Amount', store=False) 

    @api.depends('invoice_date')
    def _compute_report_invoice_date(self):
        for move in self:
            if move.invoice_date:
                move.report_invoice_date_month = move.invoice_date.strftime('%Y%m')
                move.report_invoice_date_day = move.invoice_date.strftime('%d')

    @api.depends('partner_id.tax_contributor_type')
    def _compute_report_vat_type(self):
        for move in self:
            if move.partner_id.tax_contributor_type in ['1']:
                move.report_vat_type = '1'
            else:
                move.report_vat_type = '2'
    
    @api.depends('invoice_line_ids')
    def  _compute_service_consumable_amount(self):
        for move in self:
            if move.invoice_line_ids:
                service_amount = 0
                consumable_amount = 0
                for invoice_line_id in move.invoice_line_ids:
                    #logging.warning("{0}".format(invoice_line_id.))
                    if invoice_line_id.product_id.type in ['consu', 'product']:
                        consumable_amount += invoice_line_id.amount_currency
                    elif invoice_line_id.product_id.type in ['service']:
                        service_amount += invoice_line_id.amount_currency
                move.report_service_amount = service_amount
                move.report_consumable_amount = consumable_amount