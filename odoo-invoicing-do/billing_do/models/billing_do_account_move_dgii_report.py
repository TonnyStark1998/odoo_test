import logging as log
from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

class BillingDoAccountMoveDgiiReport(models.Model):
    _inherit = "account.move"

    # Common fields between DGII reports
    report_vat = fields.Char(related='partner_id.vat', string='Tax Contributor ID', store=False)
    report_vat_type = fields.Char(compute='_compute_report_vat_type', string='Tax Contributor Type', store=False)
    report_move = fields.Char(string='Tax Receipt Number', compute='_compute_move', store=False)
    report_move_reversed = fields.Char(string='Tax Receipt Reversed', compute='_compute_move', store=False)
    report_isc_amount = fields.Monetary(string='ISC Amount', store=False)

    # Fields for DGII report 606
    report_bill_date_month = fields.Char(string='Bill Date Month', compute='_compute_report_invoice_date')
    report_bill_date_day = fields.Char(string='Bill Date Day', compute='_compute_report_invoice_date')
    report_bill_payment_date_month = fields.Char(string='Payment Date Month', compute='_compute_report_bill_payment_date', store=False)
    report_bill_payment_date_day = fields.Char(string='Payment Date Day', compute='_compute_report_bill_payment_date', store=False)
    report_bill_service_amount = fields.Monetary(string='Service Amount', default=0.0, currency_field='company_currency_id', compute='_compute_service_consumable_amount')
    report_bill_consumable_amount = fields.Monetary(string='Consumable Amount', default=0.0, currency_field='company_currency_id', compute='_compute_service_consumable_amount')
    report_bill_total_amount = fields.Monetary(string='Total Amount', default=0.0, compute='_compute_report_total_amount', store=False)
    report_bill_tax_amount = fields.Monetary(string='Tax Amount', currency_field='company_currency_id', compute='_compute_report_bill_tax_amount', default=0.0)
    # Fields for DGII report 606 (NOT IN USE RIGHT NOW!)
    report_bill_itbis_held_amount = fields.Monetary(string='ITBIS Held Amount', store=False)
    report_bill_itbis_proportional_amount = fields.Monetary(string='ITBIS Proportional Amount', store=False)
    report_bill_itbis_expense_amount = fields.Monetary(string='ITBIS Expense Amount', store=False)
    report_bill_itbis_ahead_amount = fields.Monetary(string='ITBIS Ahead Amount', store=False)
    report_bill_itbis_purchases_amount = fields.Monetary(string='ITBIS Purchases Amount', store=False)
    report_bill_isr_type = fields.Char(string='ISR Type', store=False)
    report_bill_isr_held_amount = fields.Monetary(string='ISR Held Amount', store=False)
    report_bill_isr_purchases_amount = fields.Monetary(string='ISR Purchases Amount', store=False)
    report_bill_other_taxes_amount = fields.Monetary(string='Bill Other Taxes Amount', store=False)
    report_bill_legaltip_amount = fields.Monetary(string='Bill Legal Tip Amount', store=False)

    # Fields for DGII report 607
    report_invoice_date = fields.Char(string='Invoice Date Month', compute='_compute_report_invoice_date')
    # Fields for DGII report 607 (NOT IN USE RIGHT NOW!)
    report_invoice_held_date = fields.Char(string='Invoice Held Date', default='')
    report_invoice_itbis_held_by_thirdparty_amount = fields.Monetary(string='ITBIS Held By ThirdParty Amount', default=0.0)
    report_invoice_itbis_perceived_amount = fields.Monetary(string='ITBIS Perceived Amount', default=0.0)
    report_invoice_isr_held_by_thirdparty_amount = fields.Monetary(string='ISR Held By ThirdParty Amount', default=0.0)
    report_invoice_isr_perceived_amount = fields.Monetary(string='ISR Perceived Amount', default=0.0)
    report_invoice_other_taxes_amount = fields.Monetary(string='Invoice Other Taxes Amount', default=0.0)
    report_invoice_legaltip_amount = fields.Monetary(string='Invoice Legal Tip Amount', store=False)
    report_invoice_cash_amount = fields.Monetary(string='Cash Amount', store=False)
    report_invoice_bank_amount = fields.Monetary(string='Bank Amount', store=False)
    report_invoice_credit_debit_card_amount = fields.Monetary(string='Credit/Debit Card Amount', store=False)
    report_invoice_credit_sale_amount = fields.Monetary(string='Credit Sale Amount', store=False)
    report_invoice_gift_amount = fields.Monetary(string='Gift Certificates Amount', store=False)
    report_invoice_permute_amount = fields.Monetary(string='Permute Amount', store=False)
    report_invoice_other_sale_way_amount = fields.Monetary(string='Other Sale Way Amount', store=False)

    # Account Move DGII Reports - Compute Field's Functions
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
                itbis_tax_amount = 0
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

    @api.depends('line_ids')
    def _compute_report_bill_tax_amount(self):
        for move in self:
            tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
            tax_balance_multiplicator = -1 if move.is_inbound(True) else 1

            res = {}
            # There are as many tax line as there are repartition lines
            done_taxes = set()
            for line in tax_lines:
                res.setdefault(line.tax_line_id.tax_group_id.name, {'base': 0.0, 'amount': 0.0})
                res[line.tax_line_id.tax_group_id.name]['amount'] += tax_balance_multiplicator * (line.amount_currency if line.currency_id else line.balance)
                tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    if line.currency_id and line.company_currency_id and line.currency_id != line.company_currency_id:
                        amount = line.company_currency_id._convert(line.tax_base_amount, line.currency_id, line.company_id, line.date or fields.Date.today())
                    else:
                        amount = line.tax_base_amount
                    res[line.tax_line_id.tax_group_id.name]['base'] += amount
                    # The base should be added ONCE
                    done_taxes.add(tax_key_add_base)
            for key, value in res.items():
                log.info("[KCS] [DEBUG] Key: {0} | Value: {1}".format(key, value))
                if key == "ITBIS":
                    move.report_bill_tax_amount = value["amount"]
                elif key == "ISC":
                    move.report_isc_amount = value["amount"]
                elif key == "Otros Impuestos":
                    move.report_bill_other_taxes_amount = value["amount"]
                elif key == "Propina":
                    move.report_bill_legaltip_amount = value["amount"]
            if not move.report_bill_tax_amount:
                move.report_bill_tax_amount = 0.0

    @api.depends('report_bill_payment_date_month','report_bill_payment_date_month')
    def _compute_report_bill_payment_date(self):
        for move in self:
            if not move.amount_residual > 0:
                _last_payment_date = move.get_last_payment_date()
                move.report_bill_payment_date_month = '' if not _last_payment_date else _last_payment_date.strftime('%Y%m')
                move.report_bill_payment_date_day = '' if not _last_payment_date else _last_payment_date.strftime('%d')
            else:
                move.report_bill_payment_date_month = ''
                move.report_bill_payment_date_day = ''
    
    @api.depends('name', 'reversal_move_id')
    def _compute_move(self):
        for move in self:
            if move.reversal_move_id:
                move.report_move = move.reversal_move_id.name
                move.report_move_reversed = move.ncf
            else:
                move.report_move = move.ncf
                move.report_move_reversed = ''
    
    @api.depends('amount_total')
    def _compute_report_total_amount(self):
        for move in self:
            move.report_bill_total_amount = move.amount_total