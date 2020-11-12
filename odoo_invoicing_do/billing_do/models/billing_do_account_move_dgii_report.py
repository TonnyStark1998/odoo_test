import logging as log
from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

class BillingDoAccountMoveDgiiReport(models.Model):
    _inherit = "account.move"

    # Common fields between DGII reports
    report_vat = fields.Char(related='partner_id.vat', string='Tax Contributor ID')
    report_vat_type = fields.Char(string='Tax Contributor Type')
    report_move = fields.Char(string='Tax Receipt Number')
    report_move_reversed = fields.Char(string='Tax Receipt Reversed')
    report_isc_amount = fields.Monetary(string='ISC Amount')

    # Fields for DGII report 606
    report_bill_date_month = fields.Char(string='Bill Date Month')
    report_bill_date_day = fields.Char(string='Bill Date Day')
    report_bill_payment_date_month = fields.Char(string='Payment Date Month')
    report_bill_payment_date_day = fields.Char(string='Payment Date Day')
    report_bill_service_amount = fields.Monetary(string='Service Amount', default=0.0, currency_field='company_currency_id')
    report_bill_consumable_amount = fields.Monetary(string='Consumable Amount', default=0.0, currency_field='company_currency_id')
    report_bill_total_amount = fields.Monetary(string='Total Amount', default=0.0)
    report_bill_tax_amount = fields.Monetary(string='Tax Amount', currency_field='company_currency_id', default=0.0)
    # Fields for DGII report 606 (NOT IN USE RIGHT NOW!)
    report_bill_itbis_held_amount = fields.Monetary(string='ITBIS Held Amount')
    report_bill_itbis_proportional_amount = fields.Monetary(string='ITBIS Proportional Amount')
    report_bill_itbis_expense_amount = fields.Monetary(string='ITBIS Expense Amount')
    report_bill_itbis_ahead_amount = fields.Monetary(string='ITBIS Ahead Amount')
    report_bill_itbis_purchases_amount = fields.Monetary(string='ITBIS Purchases Amount')
    report_bill_isr_type = fields.Char(string='ISR Type')
    report_bill_isr_held_amount = fields.Monetary(string='ISR Held Amount')
    report_bill_isr_purchases_amount = fields.Monetary(string='ISR Purchases Amount')
    report_bill_other_taxes_amount = fields.Monetary(string='Bill Other Taxes Amount')
    report_bill_legaltip_amount = fields.Monetary(string='Bill Legal Tip Amount')

    # Fields for DGII report 607
    report_invoice_date = fields.Char(string='Invoice Date Month')
    # Fields for DGII report 607 (NOT IN USE RIGHT NOW!)
    report_invoice_held_date = fields.Char(string='Invoice Held Date')
    report_invoice_itbis_held_by_thirdparty_amount = fields.Monetary(string='ITBIS Held By ThirdParty Amount')
    report_invoice_itbis_perceived_amount = fields.Monetary(string='ITBIS Perceived Amount')
    report_invoice_isr_held_by_thirdparty_amount = fields.Monetary(string='ISR Held By ThirdParty Amount')
    report_invoice_isr_perceived_amount = fields.Monetary(string='ISR Perceived Amount')
    report_invoice_other_taxes_amount = fields.Monetary(string='Invoice Other Taxes Amount')
    report_invoice_legaltip_amount = fields.Monetary(string='Invoice Legal Tip Amount')
    report_invoice_cash_amount = fields.Monetary(string='Cash Amount')
    report_invoice_bank_amount = fields.Monetary(string='Bank Amount')
    report_invoice_credit_debit_card_amount = fields.Monetary(string='Credit/Debit Card Amount')
    report_invoice_credit_sale_amount = fields.Monetary(string='Credit Sale Amount')
    report_invoice_gift_amount = fields.Monetary(string='Gift Certificates Amount')
    report_invoice_permute_amount = fields.Monetary(string='Permute Amount')
    report_invoice_other_sale_way_amount = fields.Monetary(string='Other Sale Way Amount')

    # Account Move DGII Reports - Compute Field's Functions
    # @api.depends('date')
    # def _compute_report_invoice_date(self):
    #     for move in self:
    #         move.report_bill_date_month = ''
    #         move.report_bill_date_day = ''
    #         move.report_invoice_date = ''

    # @api.depends('partner_id.tax_contributor_type')
    # def _compute_report_vat_type(self):
    #     for move in self:
    #         if move.partner_id.tax_contributor_type in ['1']:
    #             move.report_vat_type = '1'
    #         else:
    #             move.report_vat_type = '2'
    
    # @api.depends('invoice_line_ids')
    # def _compute_service_consumable_amount(self):
    #     for move in self:
    #         move.report_bill_service_amount = 0.0
    #         move.report_bill_consumable_amount = 0.0
    #         move.report_bill_total_amount = 0.0

    # @api.depends('line_ids')
    # def _compute_report_bill_tax_amount(self):
    #     for move in self:
    #         move.report_isc_amount = 0.0
    #         move.report_bill_other_taxes_amount = 0.0
    #         move.report_bill_legaltip_amount = 0.0
    #         move.report_bill_tax_amount = 0.0

    # @api.depends('report_bill_payment_date_month','report_bill_payment_date_month')
    # def _compute_report_bill_payment_date(self):
    #     for move in self:
    #         move.report_bill_payment_date_month = ''
    #         move.report_bill_payment_date_day = ''
    
    # @api.depends('name', 'reversal_move_id')
    # def _compute_move(self):
    #     for move in self:
    #         move.report_move = ''
    #         move.report_move_reversed = ''
    
    # @api.depends('line_ids')
    # def _compute_report_bill_itbis_held_amount(self):
    #     for move in self:
    #         move.report_bill_itbis_held_amount = 0.0
    #         move.report_invoice_itbis_held_by_thirdparty_amount = 0.0
    #         move.report_bill_isr_held_amount = 0.0
    #         move.report_invoice_isr_held_by_thirdparty_amount = 0.0