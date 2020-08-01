import logging as log
from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

class BillingDoAccountMoveDgiiReport(models.Model):
    _inherit = "account.move"

    # Common fields between DGII reports
    report_vat = fields.Char(related='partner_id.vat', string='Tax Contributor ID', store=False)
    report_vat_type = fields.Char(compute='_compute_report_vat_type', string='Tax Contributor Type', store=False)
    report_reversed_move = fields.Char(related='reversal_move_id.name', string='Tax Receipt Reversed', store=False)
    report_legaltip_amount = fields.Monetary(string='Legal Tip Amount', store=False)
    report_isc_amount = fields.Monetary(string='ISC Amount', store=False)

    # Fields for DGII report 606
    report_bill_date_month = fields.Char(string='Bill Date Month', compute='_compute_report_invoice_date')
    report_bill_date_day = fields.Char(string='Bill Date Day', compute='_compute_report_invoice_date')
    report_bill_payment_date_month = fields.Char(string='Payment Date Month', store=False)
    report_bill_payment_date_day = fields.Char(string='Payment Date Day', store=False)
    report_bill_service_amount = fields.Monetary(string='Service Amount', default=0.0, currency_field='company_currency_id', compute='_compute_service_consumable_amount')
    report_bill_consumable_amount = fields.Monetary(string='Consumable Amount', default=0.0, currency_field='company_currency_id', compute='_compute_service_consumable_amount')
    report_bill_total_amount = fields.Monetary(string='Total Amount', default=0.0, store=False)
    report_bill_tax_amount = fields.Monetary(string='Tax Amount', currency_field='company_currency_id', compute='_compute_report_bill_tax_amount')
    # Fields for DGII report 606 (NOT IN USE RIGHT NOW!)
    report_bill_itbis_billed_amount = fields.Monetary(string='ITBIS Billed Amount', store=False)
    report_bill_itbis_held_amount = fields.Monetary(string='ITBIS Held Amount', store=False)
    report_bill_itbis_proportional_amount = fields.Monetary(string='ITBIS Proportional Amount', store=False)
    report_bill_itbis_expense_amount = fields.Monetary(string='ITBIS Expense Amount', store=False)
    report_bill_itbis_ahead_amount = fields.Monetary(string='ITBIS Ahead Amount', store=False)
    report_bill_itbis_purchases_amount = fields.Monetary(string='ITBIS Purchases Amount', store=False)
    report_bill_isr_type = fields.Char(string='ISR Type', store=False)
    report_bill_isr_held_amount = fields.Monetary(string='ISR Held Amount', store=False)
    report_bill_isr_purchases_amount = fields.Monetary(string='ISR Purchases Amount', store=False)
    report_bill_other_taxes_amount = fields.Monetary(string='Other Taxes Amount', store=False)
    report_bill_legaltip_amount = fields.Monetary(string='Legal Tip Amount', store=False)

    # Fields for DGII report 607
    report_invoice_date = fields.Char(string='Invoice Date Month', compute='_compute_report_invoice_date')
    # Fields for DGII report 607 (NOT IN USE RIGHT NOW!)
    report_invoice_held_date = fields.Char(string='Invoice Held Date', default='')
    report_invoice_itbis_held_by_thirdparty_amount = fields.Monetary(string='ITBIS Held By ThirdParty Amount', default=0.0)
    report_invoice_itbis_perceived_amount = fields.Monetary(string='ITBIS Perceived Amount', default=0.0)
    report_invoice_isr_held_by_thirdparty_amount = fields.Monetary(string='ISR Held By ThirdParty Amount', default=0.0)
    report_invoice_isr_perceived_amount = fields.Monetary(string='ISR Perceived Amount', default=0.0)
    report_invoice_other_taxes_amount = fields.Monetary(string='Other Taxes Amount', default=0.0)
    report_invoice_legaltip_amount = fields.Monetary(string='Legal Tip Amount', store=False)
    report_invoice_cash_amount = fields.Monetary(string='Cash Amount', store=False)
    report_invoice_bank_amount = fields.Monetary(string='Bank Amount', store=False)
    report_invoice_credit_debit_card_amount = fields.Monetary(string='Credit/Debit Card Amount', store=False)
    report_invoice_credit_sale_amount = fields.Monetary(string='Credit Sale Amount', store=False)
    report_invoice_gift_amount = fields.Monetary(string='Gift Certificates Amount', store=False)
    report_invoice_permute_amount = fields.Monetary(string='Permute Amount', store=False)
    report_invoice_other_sale_way_amount = fields.Monetary(string='Other Sale Way Amount', store=False)

    # Account Move - Compute Field's Functions
    @api.depends('invoice_date')
    def _compute_report_invoice_date(self):
        for move in self:
            if move.invoice_date:
                move.report_bill_date_month = move.invoice_date.strftime('%Y%m')
                move.report_bill_date_day = move.invoice_date.strftime('%d')
                move.report_invoice_date = move.invoice_date.strftime('%Y%m%d')

    @api.depends('partner_id.tax_contributor_type')
    def _compute_report_vat_type(self):
        for move in self:
            if move.partner_id.tax_contributor_type in ['1']:
                move.report_vat_type = '1'
            else:
                move.report_vat_type = '2'
    
    @api.depends('invoice_line_ids')
    def _compute_service_consumable_amount(self):
        for move in self:
            if move.invoice_line_ids:
                service_amount = 0
                consumable_amount = 0
                for invoice_line_id in move.invoice_line_ids:
                    unit_price = invoice_line_id.price_subtotal
                    if invoice_line_id.currency_id:
                        unit_price = invoice_line_id.currency_id._convert(unit_price, self.env.company.currency_id, self.env.company, move.invoice_date, True)
                    if invoice_line_id.product_id.type in ['consu', 'product']:
                        consumable_amount += unit_price
                    elif invoice_line_id.product_id.type in ['service']:
                        service_amount += unit_price
                move.report_bill_service_amount = service_amount
                move.report_bill_consumable_amount = consumable_amount
    
    @api.depends('amount_tax')
    def _compute_report_bill_tax_amount(self):
        for move in self:
            if move.amount_tax and (move.currency_id.name != self.env.company.currency_id.name):
                move.report_bill_tax_amount = move.currency_id._convert(move.amount_tax, self.env.company.currency_id, self.env.company, move.invoice_date, True)
            else:
                move.report_bill_tax_amount = move.amount_tax