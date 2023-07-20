# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

import datetime, \
        calendar, \
        logging as log, \
        json

class BillingDoTaxReportItem607(models.Model):
    _name = 'billing.do.tax.report.item.607'
    _description = 'Billing DO - Tax Report 607'
    _check_company_auto = True
    _inherit = 'billing.do.tax.report.item.common'
    _order = 'date_invoice desc'

    company_id = fields.Many2one(string='Company',
                                    comodel_name='res.company',
                                    default=lambda self: self.env.company.id)

    # Model fields
    income_type = fields.Selection(selection=[
                                                ('01', '01 - Ingresos por Operaciones (No Financieros)'),
                                                ('02', '02 - Ingresos Financieros'),
                                                ('03', '03 - Ingresos Extraordinarios'),
                                                ('04', '04 - Ingresos por Arrendamientos'),
                                                ('05', '05 - Ingresos por Venta de Activo Depreciable'),
                                                ('06', '06 - Otros Ingresos')
                                            ], 
                                    string='Income Type')

    date_invoice = fields.Char(string='Invoice Date')
    date_amount_held = fields.Char(string='Invoice Held Date')

    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount Signed',
                                                default=0.00)
    amount_tax_signed = fields.Monetary(string='Tax Amount Signed',
                                            default=0.00)
    amount_cash = fields.Monetary(string='Cash Amount',
                                    default=0.00)
    amount_bank = fields.Monetary(string='Bank Amount',
                                    default=0.00)
    amount_credit_debit_card = fields.Monetary(string='Credit/Debit Card Amount',
                                                default=0.00)
    amount_credit_sale = fields.Monetary(string='Credit Sale Amount',
                                            default=0.00)
    amount_other_sale_way = fields.Monetary(string='Other Sale Amount',
                                                default=0.00)

    # Fields NOT IN USE!!!
    amount_itbis_perceived = fields.Monetary(string='ITBIS Perceived Amount',
                                                default=0.00)
    amount_isr_perceived = fields.Monetary(string='ISR Perceived Amount',
                                            default=0.00)
    amount_other_taxes = fields.Monetary(string='Invoice Other Taxes Amount',
                                            default=0.00)
    amount_legaltip = fields.Monetary(string='Legal Tip Amount',
                                        default=0.00)
    amount_gift = fields.Monetary(string='Gift Amount',
                                    default=0.00)
    amount_permute = fields.Monetary(string='Permute Amount',
                                        default=0.00)

    def generate_item(self, move, tax_report):
        return {}

    def generate_items(self, tax_report, tax_term_date):

        moves = self._get_items(tax_report, tax_term_date)
        
        for move in moves:
            tax_report_item = super(BillingDoTaxReportItem607, self)\
                                    .generate_item(move, tax_report)

            tax_report_item\
                .update(self.generate_item(move, tax_report))

            # Set the invoice amount without any taxes
            if move.amount_untaxed_signed:
                tax_report_item['amount_untaxed_signed'] = self._convert_amount_to_dop(move.company_id.currency_id,
                                                                                        move.amount_untaxed_signed,
                                                                                        move.invoice_date,
                                                                                        move.company_id
                                                                                    )
            
            # Set the amount for the taxes charge to this invoice
            if move.amount_tax_signed:
                tax_report_item['amount_tax_signed'] = self._convert_amount_to_dop(move.company_id.currency_id,
                                                                                    move.amount_tax_signed,
                                                                                    move.invoice_date,
                                                                                    move.company_id
                                                                                )

            # Set the income type for this move if the move has an income type value
            if move.income_type:
                tax_report_item['income_type'] = move.income_type

            # Set the date for the report separating the year and month from the day of the invoice date
            if move.invoice_date:
                tax_report_item['date_invoice'] = move.invoice_date\
                                                        .strftime('%Y%m%d')

            # Get all reconciled info for the move, these are the payments.
            _reconciled_values = move.invoice_payments_widget['content']

            tax_report_item.update(self._get_held_amounts(move.line_ids
                                                            + self._get_payment_lines(_reconciled_values)))
            
            tax_report_item.update(self._calculate_payments_amounts(move, _reconciled_values))

            if move.payment_state in ['paid']:

                if tax_report_item['held_amount_itbis'] > 0 \
                        or tax_report_item['held_amount_isr'] > 0:

                    _last_payment_date = self._get_payment_last_date(_reconciled_values)

                    tax_report_item['date_amount_held'] = \
                            _last_payment_date.strftime('%Y%m%d')

            self.create(tax_report_item)
        
        return len(moves)
    
    def _calculate_payments_amounts(self, move, reconciled_values):
        tax_report_item = {
            'amount_cash': 0.00,
            'amount_bank': 0.00,
            'amount_credit_debit_card': 0.00,
            'amount_credit_sale': 0.00,
            'amount_other_sale_way': 0.00,
        }

        _payment_amount = 0.0

        if move.payment_state in ['paid']:
            for _payment in reconciled_values:
                _payment_type = self._get_payment_type(self.env['account.move.line']
                                                            .search([('id', '=', _payment['account_payment_id'])])
                                                            .journal_id)

                _payment_amount = self._convert_amount_to_dop(self.env['res.currency']
                                                                    .search([('id', '=', _payment['currency_id'])]),
                                                        _payment['amount'],
                                                        move.invoice_date,
                                                        move.company_id
                                                    )

                if _payment_type in ['01']:
                    tax_report_item['amount_cash'] += _payment_amount

                elif _payment_type in ['02']:
                    tax_report_item['amount_bank'] += _payment_amount

                elif _payment_type in ['03']:
                    tax_report_item['amount_credit_debit_card'] += _payment_amount
                
                else:
                    tax_report_item['amount_other_sale_way'] += _payment_amount
        else:
            _payment_amount = self._convert_amount_to_dop(move.currency_id,
                                                            move.amount_total,
                                                            move.invoice_date,
                                                            move.company_id
                                                        )
            
            tax_report_item['amount_credit_sale'] \
                = _payment_amount

        return tax_report_item

    def _get_held_amounts(self, move_lines):
        tax_report_item = {
            'held_amount_itbis': 0.00,
            'held_amount_isr': 0.00
        }
        
        for move_line in move_lines:
            _line_amount = self._convert_amount_to_dop(move_line.move_id.company_id.currency_id,
                                                        move_line.credit + move_line.debit,
                                                        move_line.move_id.invoice_date or 
                                                            move_line.move_id.date,
                                                        move_line.move_id.company_id
                                                    )

            if move_line.account_id.withholding_tax_type in ["RET-ITBIS-607"]:
                tax_report_item['held_amount_itbis'] += _line_amount
            elif move_line.account_id.withholding_tax_type in ["RET-ISR-607"]:
                tax_report_item['held_amount_isr'] += _line_amount

        return tax_report_item

    def _get_items(self, tax_report, tax_term_date):
        tax_term_date_end = datetime\
                                .date(int(tax_term_date.year), 
                                        int(tax_term_date.month), 
                                        calendar
                                            .monthrange(int(tax_term_date.year),
                                                        int(tax_term_date.month))[1])

        _tmp_moves = super(BillingDoTaxReportItem607, self)\
                        .generate_items(tax_report, tax_term_date)
        _moves = _tmp_moves.filtered(lambda move:
                                        move.move_type in ['out_invoice', 'out_refund']
                                            and move.company_id.id == self.env.company.id
                                            and move.invoice_date >= tax_term_date
                                            and move.invoice_date <= tax_term_date_end)

        _moves += _tmp_moves.filtered(lambda move:
                                        move.move_type in ['out_invoice', 'out_refund']
                                            and move.invoice_date < tax_term_date
                                            and move.payment_state in ['paid']
                                            and move.invoice_payments_widget
                                            and move.invoice_payments_widget['content']
                                            and any(payment['date'] >= tax_term_date
                                                        and payment['date'] <= tax_term_date_end
                                                        and any(move_line.account_id
                                                                    .withholding_tax_type in ['RET-ITBIS-607', 
                                                                                                'RET-ISR-607']
                                                            for move_line in self.env['account.move']
                                                                .browse(payment['move_id'])
                                                                .line_ids)
                                                    for payment in move.invoice_payments_widget['content']))

        return _moves