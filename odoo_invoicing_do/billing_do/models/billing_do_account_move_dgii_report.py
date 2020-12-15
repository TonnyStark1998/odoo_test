import logging as log
import datetime as datetime
from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils

class BillingDoAccountMoveDgiiReport(models.Model):
    _inherit = "account.move"

    # Common fields between DGII reports
    report_vat = fields.Char(related='partner_id.vat', 
                                string='Tax Contributor ID')
    report_vat_type = fields.Char(string='Tax Contributor Type',
                                    compute='_compute_report_vat_type',
                                    store=True
                                )
    report_move = fields.Char(string='Tax Receipt Number',
                                compute='_compute_move_name',
                                store=True
                            )
    report_move_reversed = fields.Char(string='Tax Receipt Reversed',
                                        compute='_compute_move_name',
                                        store=True
                                    )
    report_isc_amount = fields.Monetary(string='ISC Amount')

    # Fields for DGII report 606
    report_bill_date_month = fields.Char(string='Bill Date Month',
                                            compute='_compute_report_dates',
                                            store=True)
    report_bill_date_day = fields.Char(string='Bill Date Day',
                                        compute='_compute_report_dates',
                                        store=True
                                    )
    report_bill_payment_date_month = fields.Char(string='Payment Date Month',
                                                    compute='_compute_report_held_values',
                                                    store=True
                                                )
    report_bill_payment_date_day = fields.Char(string='Payment Date Day',
                                                compute='_compute_report_held_values',
                                                store=True
                                            )
    report_bill_service_amount = fields.Monetary(string='Service Amount', 
                                                    default=0.0, 
                                                    currency_field='company_currency_id',
                                                    compute='_compute_service_consumable_amount',
                                                    store=True
                                                )
    report_bill_consumable_amount = fields.Monetary(string='Consumable Amount', 
                                                    default=0.0, 
                                                    currency_field='company_currency_id',
                                                    compute='_compute_service_consumable_amount',
                                                    store=True
                                                )
    report_bill_total_amount = fields.Monetary(string='Total Amount', 
                                                default=0.0,
                                                compute='_compute_service_consumable_amount',
                                                store=True
                                            )
    report_bill_tax_amount = fields.Monetary(string='Tax Amount', 
                                                currency_field='company_currency_id', 
                                                default=0.0,
                                                compute='_compute_report_bill_tax_amount',
                                                store=True
                                            )
    # Fields for DGII report 606 (NOT IN USE RIGHT NOW!)
    report_bill_itbis_held_amount = fields.Monetary(string='ITBIS Held Amount',
                                                        compute='_compute_report_held_values',
                                                        default=0.0,
                                                        store=True
                                                    )
    report_bill_itbis_proportional_amount = fields.Monetary(string='ITBIS Proportional Amount')
    report_bill_itbis_expense_amount = fields.Monetary(string='ITBIS Expense Amount')
    report_bill_itbis_ahead_amount = fields.Monetary(string='ITBIS Ahead Amount')
    report_bill_itbis_purchases_amount = fields.Monetary(string='ITBIS Purchases Amount')
    report_bill_isr_type = fields.Char(string='ISR Type')
    report_bill_isr_held_amount = fields.Monetary(string='ISR Held Amount',
                                                    compute='_compute_report_held_values',
                                                    default=0.0,
                                                    store=True
                                                )
    report_bill_isr_purchases_amount = fields.Monetary(string='ISR Purchases Amount')
    report_bill_other_taxes_amount = fields.Monetary(string='Bill Other Taxes Amount')
    report_bill_legaltip_amount = fields.Monetary(string='Bill Legal Tip Amount')
    report_bill_payment_type = fields.Selection(selection=[('01', '01 - EFECTIVO'),
                                                        ('02', '02 - CHEQUES/TRANSFERENCIAS/DEPÓSITO'),
                                                        ('03', '03 - TARJETA CRÉDITO/DÉBITO'),
                                                        ('04', '04 - COMPRA A CREDITO'),
                                                        ('05', '05 -  PERMUTA'),
                                                        ('06', '06 - NOTA DE CREDITO'),
                                                        ('07', '07 - MIXTO'),
                                                    ],
                                                string='Payment Type',
                                                compute='_compute_report_held_values',
                                                store=True
                                            )

    # Fields for DGII report 607
    report_invoice_date_month = fields.Char(string='Invoice Date Month',
                                                compute='_compute_report_dates',
                                                store=True
                                            )
    # Fields for DGII report 607 (NOT IN USE RIGHT NOW!)
    report_invoice_held_date = fields.Char(string='Invoice Held Date',
                                            compute='_compute_report_held_values',
                                            store=True
                                        )
    report_invoice_itbis_held_by_thirdparty_amount = fields.Monetary(string='ITBIS Held By ThirdParty Amount', 
                                                                        default=0.0,
                                                                        compute='_compute_report_held_values',
                                                                        store=True
                                                                    )
    report_invoice_itbis_perceived_amount = fields.Monetary(string='ITBIS Perceived Amount')
    report_invoice_isr_held_by_thirdparty_amount = fields.Monetary(string='ISR Held By ThirdParty Amount',
                                                                    default=0.0,
                                                                    compute='_compute_report_held_values',
                                                                    store=True
                                                                )
    report_invoice_isr_perceived_amount = fields.Monetary(string='ISR Perceived Amount')
    report_invoice_other_taxes_amount = fields.Monetary(string='Invoice Other Taxes Amount')
    report_invoice_legaltip_amount = fields.Monetary(string='Invoice Legal Tip Amount')
    report_invoice_cash_amount = fields.Monetary(string='Cash Amount',
                                                    compute='_compute_report_held_values',
                                                    store=True
                                                )
    report_invoice_bank_amount = fields.Monetary(string='Bank Amount',
                                                    compute='_compute_report_held_values',
                                                    store=True
                                                )
    report_invoice_credit_debit_card_amount = fields.Monetary(string='Credit/Debit Card Amount',
                                                                compute='_compute_report_held_values',
                                                                store=True
                                                            )
    report_invoice_credit_sale_amount = fields.Monetary(string='Credit Sale Amount',
                                                        compute='_compute_report_held_values',
                                                        store=True
                                                        )
    report_invoice_gift_amount = fields.Monetary(string='Gift Certificates Amount')
    report_invoice_permute_amount = fields.Monetary(string='Permute Amount')
    report_invoice_other_sale_way_amount = fields.Monetary(string='Other Sale Way Amount')

    # Account Move DGII Reports - Compute Field's Functions
    @api.depends('name')
    def _compute_move_name(self):
        for move in self:
            move_name = ''
            move_reversed_name = ''
            if move.type in ['out_invoice']:
                move_name = move.name
            elif move.type in ['out_refund']:
                move_name = move.name
                move_reversed_name = move.reversed_entry_id.name
            elif move.type in ['in_invoice']:
                move_name = move.ncf
            elif move.type in ['in_refund']:
                move_name = move.reversal_move_id.name
                move_reversed_name = move.ncf
            move.report_move = move_name
            move.report_move_reversed = move_reversed_name

    @api.depends('date')
    def _compute_report_dates(self):
        for move in self:
            bill_date_month = ''
            bill_date_day = ''
            invoice_date_month = ''
            if move.date and move.type not in ['entry']:
                bill_date_month = move.date.strftime('%Y%m')
                bill_date_day = move.date.strftime('%d')
                invoice_date_month = move.date.strftime('%Y%m%d')
            move.report_bill_date_month = bill_date_month
            move.report_bill_date_day = bill_date_day
            move.report_invoice_date_month = invoice_date_month

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
            service_amount = 0
            consumable_amount = 0
            itbis_tax_amount = 0
            if move.invoice_line_ids:
                for invoice_line_id in move.invoice_line_ids:
                    unit_price = invoice_line_id.price_subtotal
                    if invoice_line_id.currency_id:
                        unit_price = invoice_line_id.currency_id._convert(unit_price, 
                                                                            self.env.company.currency_id, 
                                                                            self.env.company, 
                                                                            move.invoice_date, 
                                                                            True
                                                                        )
                    if invoice_line_id.product_id.type in ['consu', 'product']:
                        consumable_amount += unit_price
                    elif invoice_line_id.product_id.type in ['service']:
                        service_amount += unit_price
            move.report_bill_service_amount = service_amount
            move.report_bill_consumable_amount = consumable_amount
            move.report_bill_total_amount = service_amount + consumable_amount

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

                res[line.tax_line_id.tax_group_id.name]['amount'] += \
                            tax_balance_multiplicator \
                                * (line.amount_currency if line.currency_id else line.balance)

                tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    if line.currency_id and line.company_currency_id and line.currency_id != line.company_currency_id:
                        amount = line.company_currency_id._convert(line.tax_base_amount, 
                                                                    line.currency_id, 
                                                                    line.company_id, 
                                                                    line.date or fields.Date.today())
                    else:
                        amount = line.tax_base_amount
                    res[line.tax_line_id.tax_group_id.name]['base'] += amount
                    # The base should be added ONCE
                    done_taxes.add(tax_key_add_base)
            for key, value in res.items():
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

    @api.depends('line_ids', 'invoice_payment_state')
    def _compute_report_held_values(self):
        all_payments = self.env['account.payment'].search(args=[])
        for move in self:
            _last_payment_date = move._get_last_payment_date()
            _payment_type = '04'

            cash_amount = 0.0
            bank_amount = 0.0
            credit_debit_card_amount = 0.0
            credit_sale_amount = 0.0

            bill_itbis_held_amount = invoice_itbis_held = bill_isr_held = invoice_isr_held = 0
            reconciled_vals = move._get_reconciled_info_JSON_values()
            move_payments_ids = [payment['account_payment_id'] for payment in reconciled_vals]
            move_payments = all_payments.filtered(lambda payment: payment.id in move_payments_ids)

            payment_amount = 0.0
            for move_payment in move_payments:
                _payment_type = move._get_payment_type(move_payment)
                payment_amount += move_payment.amount

                for line in move_payment.move_line_ids:
                    if line.account_id.withholding_tax_type in ["RET-ITBIS-606"]:
                        bill_itbis_held_amount = line.credit + line.debit
                    elif line.account_id.withholding_tax_type in ["RET-ITBIS-607"]:
                        invoice_itbis_held = line.credit + line.debit
                    elif line.account_id.withholding_tax_type in ["RET-ISR-606"]:
                        bill_isr_held = line.credit + line.debit
                    elif line.account_id.withholding_tax_type in ["RET-ISR-607"]:
                        invoice_isr_held = line.credit + line.debit

            if _payment_type in ['01']:
                cash_amount = payment_amount
            elif _payment_type in ['02']:
                bank_amount = payment_amount
            elif _payment_type in ['03']:
                credit_debit_card_amount = payment_amount
            elif _payment_type in ['04']:
                credit_sale_amount = move.amount_total

            for line in move.line_ids:
                if line.account_id.withholding_tax_type in ["RET-ITBIS-606"]:
                    bill_itbis_held_amount = line.credit + line.debit
                elif line.account_id.withholding_tax_type in ["RET-ITBIS-607"]:
                    invoice_itbis_held = line.credit + line.debit
                elif line.account_id.withholding_tax_type in ["RET-ISR-606"]:
                    bill_isr_held = line.credit + line.debit
                elif line.account_id.withholding_tax_type in ["RET-ISR-607"]:
                    invoice_isr_held = line.credit + line.debit

            move.report_invoice_cash_amount = cash_amount
            move.report_invoice_bank_amount = bank_amount
            move.report_invoice_credit_debit_card_amount = credit_debit_card_amount
            move.report_invoice_credit_sale_amount = credit_sale_amount

            move.report_bill_payment_type = '04'

            move.report_invoice_held_date = ''
            move.report_bill_payment_date_month = ''
            move.report_bill_payment_date_day = ''

            move.report_bill_itbis_held_amount = ''
            move.report_bill_isr_held_amount = ''

            move.report_invoice_itbis_held_by_thirdparty_amount = ''
            move.report_invoice_isr_held_by_thirdparty_amount = ''

            if move.invoice_payment_state in ['paid']:
                move.report_bill_payment_type = _payment_type
                if _last_payment_date != datetime.date.min:
                    if invoice_isr_held > 0 or invoice_itbis_held > 0:
                        move.report_invoice_held_date = \
                            _last_payment_date if not _last_payment_date else _last_payment_date.strftime('%Y%m%d')

                    if bill_isr_held > 0 or bill_itbis_held_amount > 0:
                        move.report_bill_payment_date_month = \
                            _last_payment_date if not _last_payment_date else _last_payment_date.strftime('%Y%m')
                        move.report_bill_payment_date_day = \
                            _last_payment_date if not _last_payment_date else _last_payment_date.strftime('%d')

                move.report_bill_itbis_held_amount = bill_itbis_held_amount
                move.report_bill_isr_held_amount = bill_isr_held

                move.report_invoice_itbis_held_by_thirdparty_amount = invoice_itbis_held
                move.report_invoice_isr_held_by_thirdparty_amount = invoice_isr_held

    def _get_payment_type(self, payment):
        if payment.journal_id.type in ['cash']:
            return '01'
        elif payment.journal_id.type in ['bank']:
            return '02'
        elif payment.journal_id.type in ['credit_debit_card']:
            return '03'