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
    amount_other_sale_way = fields.Monetary(string='Other Sale Amount',
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
                tax_report_item['amount_untaxed_signed'] = move.amount_untaxed_signed
            
            # Set the amount for the taxes charge to this invoice
            if move.amount_tax_signed:
                tax_report_item['amount_tax_signed'] = move.amount_tax_signed

            # Set the income type for this move if the move has an income type value
            if move.income_type:
                tax_report_item['income_type'] = move.income_type

            # Set the date for the report separating the year and month from the day of the invoice date
            if move.invoice_date:
                tax_report_item['date_invoice'] = move.invoice_date\
                                                        .strftime('%Y%m%d')

            # Get all reconciled info for the move, these are the payments.
            _reconciled_values = move._get_reconciled_info_JSON_values()

            tax_report_item.update(self._get_held_amounts(move.line_ids
                                                            + self._get_payment_lines(_reconciled_values)))
            
            tax_report_item.update(self._calcuate_payments_amounts(move, _reconciled_values))

            if move.invoice_payment_state in ['paid']:

                if tax_report_item['held_amount_itbis'] > 0 \
                        or tax_report_item['held_amount_isr'] > 0:

                    _last_payment_date = self._get_payment_last_date(_reconciled_values)

                    tax_report_item['date_amount_held'] = \
                            _last_payment_date.strftime('%Y%m%d')

            self.create(tax_report_item)
        
        return len(moves)
    
    def _calcuate_payments_amounts(self, move, reconciled_values):
        tax_report_item = {
            'amount_cash': 0.00,
            'amount_bank': 0.00,
            'amount_credit_debit_card': 0.00,
            'amount_credit_sale': 0.00,
        }

        _payment_amount = 0.0

        if move.invoice_payment_state in ['paid']:
            for _payment in reconciled_values:
                _payment_type = self._get_payment_type(self.env['account.move.line']
                                                            .search([('id', '=', _payment['payment_id'])])
                                                            .journal_id)
                _payment_amount = _payment['amount'] \
                                    if \
                                        _payment['currency'] == 'RD$' \
                                    else \
                                        self.env['res.currency'] \
                                            .search([('name', '=', _payment['currency'])]) \
                                            ._convert(_payment['amount'],
                                                        self.env['res.currency']
                                                            .search([('name', '=', 'RD$')]),
                                                        self.env.company,
                                                        _payment['date'] \
                                                            or move.invoice_date \
                                                            or fields.Date.today(),
                                                        True)
                if _payment_type in ['01']:
                    tax_report_item['amount_cash'] += _payment_amount

                elif _payment_type in ['02']:
                    tax_report_item['amount_bank'] += _payment_amount

                elif _payment_type in ['03']:
                    tax_report_item['amount_credit_debit_card'] += _payment_amount
        else:
            if move.currency_id.name == "RD$":
                _payment_amount = move.amount_total
            else:
                _payment_amount = self.env['res.currency'] \
                                            .search([('name', '=', move.currency_id.name)]) \
                                            ._convert(move.amount_total,
                                                        self.env['res.currency']
                                                            .search([('name', '=', 'RD$')]),
                                                        self.env.company,
                                                        move.invoice_date \
                                                            or fields.Date.today(),
                                                        True)
            
            tax_report_item['amount_credit_sale'] \
                = _payment_amount

        return tax_report_item

    def _get_held_amounts(self, move_lines):
        tax_report_item = {
            'held_amount_itbis': 0.00,
            'held_amount_isr': 0.00
        }
        
        for move_line in move_lines:
            _line_amount = move_line.credit + move_line.debit

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

        _moves = super(BillingDoTaxReportItem607, self)\
                    .generate_items(tax_report, tax_term_date)\
                    .filtered(lambda move:\
                                (move.type in ['out_invoice', 'out_refund']\
                                    and ((move.company_id.id == self.env.company.id\
                                            and move.invoice_date >= tax_term_date\
                                            and move.invoice_date <= tax_term_date_end)
                                        or (move.invoice_date < tax_term_date
                                                and move.invoice_payment_state in ['paid']
                                                and any(datetime.datetime
                                                                    .strptime(payment['date'], '%Y-%m-%d') 
                                                                    .date() >= tax_term_date
                                                            and datetime.datetime
                                                                    .strptime(payment['date'], '%Y-%m-%d')
                                                                    .date() <= tax_term_date_end 
                                                        for payment in json.loads(move.invoice_payments_widget)['content'])))))

        _moves_ids = [_move_line.id for _move_line in 
                                            self.env['account.move.line']\
                                                .search([('move_id.type', 'in', ['out_invoice', 'out_refund']),
                                                            ('company_id', '=', self.env.company.id),
                                                            ('account_id.withholding_tax_type', 'in', ["RET-ISR-606", \
                                                                                                        "RET-ITBIS-606", \
                                                                                                        "RET-ISR-607", \
                                                                                                        "RET-ITBIS-607"]),
                                                            ('date', '>=', tax_term_date),
                                                            ('date', '<=', tax_term_date_end)])]

        return _moves + self.env['account.move']\
                            .browse(_moves_ids)