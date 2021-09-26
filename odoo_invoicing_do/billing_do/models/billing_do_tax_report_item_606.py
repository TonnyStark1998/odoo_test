# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

import datetime, \
        calendar, \
        logging as log

class BillingDoTaxReportItem606(models.Model):
    _name = 'billing.do.tax.report.item.606'
    _description = 'Billing DO - Tax Report 606'
    _inherit = 'billing.do.tax.report.item.common'
    _order = 'date_invoice_month, date_invoice_day desc'

    # Model fields
    date_invoice_month = fields.Char(string='Invoice Date Month')
    date_invoice_day = fields.Char(string='Invoice Date Day')

    expense_type = fields.Selection(selection=[
                                                ('01', '01 -GASTOS DE PERSONAL'),
                                                ('02', '02-GASTOS POR TRABAJOS, SUMINISTROS Y SERVICIOS'),
                                                ('03', '03-ARRENDAMIENTOS'),
                                                ('04', '04-GASTOS DE ACTIVOS FIJO'),
                                                ('05', '05 -GASTOS DE REPRESENTACIÓN'),
                                                ('06', '06 -OTRAS DEDUCCIONES ADMITIDAS'),
                                                ('07', '07 -GASTOS FINANCIEROS'),
                                                ('08', '08 -GASTOS EXTRAORDINARIOS'),
                                                ('09', '09 -COMPRAS Y GASTOS QUE FORMARAN PARTE DEL COSTO DE VENTA'),
                                                ('10', '10 -ADQUISICIONES DE ACTIVOS'),
                                                ('11', '11- GASTOS DE SEGUROS'),
                                            ], 
                                        string='Expense Type'
                                    )

    consumable_amount = fields.Monetary(string='Consumable Amount',
                                            default=0.00)
    service_amount = fields.Monetary(string='Service Amount',
                                            default=0.00)
    total_amount = fields.Monetary(string='Total Amount',
                                            default=0.00)

    date_payment_month = fields.Char(string='Payment Date Month')
    date_payment_day = fields.Char(string='Payment Date Day')
    payment_type = fields.Selection(selection=[('01', '01 - EFECTIVO'),
                                                        ('02', '02 - CHEQUES/TRANSFERENCIAS/DEPÓSITO'),
                                                        ('03', '03 - TARJETA CRÉDITO/DÉBITO'),
                                                        ('04', '04 - COMPRA A CREDITO'),
                                                        ('05', '05 -  PERMUTA'),
                                                        ('06', '06 - NOTA DE CREDITO'),
                                                        ('07', '07 - MIXTO'),
                                                    ],
                                        string='Payment Type'
                                    )

    tax_amount = fields.Monetary(string='Tax Amount', 
                                    default=0.0)
    other_taxes_amount = fields.Monetary(string='Other Taxes Amount', 
                                    default=0.0)
    legaltip_amount = fields.Monetary(string='Legal Tip Amount', 
                                    default=0.0)

    # Fields NOT IN USE!!!
    amount_isr_purchases = fields.Monetary(string='ISR Purchases Amount',
                                            default=0.00)
    amount_itbis_proportional = fields.Monetary(string='ITBIS Proportional Amount',
                                                    default=0.00)
    amount_itbis_expenses = fields.Monetary(string='ITBIS Expenses Amount',
                                                default=0.00)
    amount_itbis_ahead = fields.Monetary(string='ITBIS Ahead Amount',
                                            default=0.00)
    amount_itbis_purchases = fields.Monetary(string='ITBIS Purchases Amount',
                                                default=0.00)

    isr_type = fields.Char(string='ISR Type',
                            default='')

    def generate_item(self, move, tax_report):
        return {
            'consumable_amount': 0.0,
            'service_amount': 0.0,
            'total_amount': 0.0,
            'tax_amount': 0.0,
            'other_taxes_amount': 0.0,
            'legaltip_amount': 0.0,
            'payment_type': '04',
        }

    def generate_items(self, tax_report, tax_term_date):

        moves = self._get_items(tax_report, tax_term_date)
        
        for move in moves:
            tax_report_item = super(BillingDoTaxReportItem606, self)\
                                    .generate_item(move, tax_report)\
            
            tax_report_item\
                    .update(self.generate_item(move, tax_report))

            tax_report_item['expense_type'] = move.expense_type

            # Set the date for the report separating the year and month from the day of the invoice date
            if move.invoice_date:
                tax_report_item['date_invoice_month'] = move.invoice_date\
                                                                .strftime('%Y%m')
                tax_report_item['date_invoice_day'] = move.invoice_date\
                                                                .strftime('%d')
            
            # Get all reconciled info for the move, these are the payments.
            _reconciled_values = move._get_reconciled_info_JSON_values()

            # Get all the move lines include the payments move lines.
            _payment_move_lines = self._get_payment_lines(_reconciled_values)

            for move_line in (_payment_move_lines):
                if move_line.account_id.withholding_tax_type in ["RET-ITBIS-606"]:
                    tax_report_item['held_amount_itbis'] += \
                        move_line.credit + move_line.debit
                elif move_line.account_id.withholding_tax_type in ["RET-ISR-606"]:
                    tax_report_item['held_amount_isr'] += \
                        move_line.credit + move_line.debit

            for move_line in (move.line_ids):
                
                if not move_line.exclude_from_invoice_tab:

                    # Calculate the consumable and services amounts
                    unit_price = move_line.price_subtotal

                    if move_line.currency_id\
                        and not move_line.currency_id.name == 'RD$':

                        unit_price = move_line.currency_id\
                                                ._convert(unit_price, 
                                                            self.env['res.currency'].search([(
                                                                'name', '=', 'RD$'
                                                            )]), 
                                                            self.env.company, 
                                                            move.invoice_date or fields.Date.today(), 
                                                            True
                                                        )
                    if move_line.product_id.type in ['consu', 'product']:
                        tax_report_item['consumable_amount'] += unit_price
                    elif move_line.product_id.type in ['service']:
                        tax_report_item['service_amount'] += unit_price

                # Calculate the tax amounts
                if move_line.tax_line_id:
                    tax = move_line.tax_line_id.tax_group_id.name
                    tax_amount = move_line.price_subtotal

                    if move_line.currency_id\
                        and not move_line.currency_id.name == 'RD$':

                        tax_amount = move_line.currency_id\
                                                ._convert(tax_amount, 
                                                            self.env['res.currency'].search([(
                                                                'name', '=', 'RD$'
                                                            )]), 
                                                            self.env.company, 
                                                            move.invoice_date or fields.Date.today(), 
                                                            True
                                                        )

                    if tax == "ITBIS":
                        tax_report_item['tax_amount'] += tax_amount
                    elif tax == "ISC":
                        tax_report_item['isc_amount'] += tax_amount
                    elif tax == "Otros Impuestos":
                        tax_report_item['other_taxes_amount'] += tax_amount
                    elif tax == "Propina":
                        tax_report_item['legaltip_amount'] += tax_amount

            tax_report_item['total_amount'] = \
                        tax_report_item['consumable_amount'] + tax_report_item['service_amount']

            if move.invoice_payment_state in ['paid']:
                for _payment_move_line in _payment_move_lines:

                    if _payment_move_line.account_internal_type \
                        in ['receivable', 'payable']:

                        tax_report_item['payment_type'] = \
                            self._get_payment_type(_payment_move_line.journal_id)

                if tax_report_item['held_amount_itbis'] > 0 \
                        or tax_report_item['held_amount_isr'] > 0:
                    
                    _last_payment_date = self._get_payment_last_date(_reconciled_values)

                    tax_report_item['date_payment_month'] = _last_payment_date.strftime('%Y%m')
                    tax_report_item['date_payment_day'] = _last_payment_date.strftime('%d')

            self.create(tax_report_item)

        return len(moves)

    def _get_items(self, tax_report, tax_term_date):
        tax_term_date_end = datetime\
                                .date(int(tax_term_date.year), 
                                        int(tax_term_date.month), 
                                        calendar
                                            .monthrange(int(tax_term_date.year),
                                                        int(tax_term_date.month))[1])

        _moves = super(BillingDoTaxReportItem606, self)\
                    .generate_items(tax_report, tax_term_date)\
                    .filtered(lambda move:\
                                move.type in ['in_invoice', 'in_refund']\
                                    and move.invoice_date >= tax_term_date\
                                    and move.invoice_date <= tax_term_date_end)

        _payment_moves_ids = []
        pay_term_line_ids = self.env['account.move.line'].filtered(lambda line: 
                                                                    line.account_id.user_type_id.type\
                                                                        in ('receivable', 'payable')\
                                                                    and line.company_id == self.env.company.id)

        partials = pay_term_line_ids.mapped('matched_debit_ids') +\
                    pay_term_line_ids.mapped('matched_credit_ids')

        for partial in partials:
            counterpart_lines = partial.debit_move_id +\
                                    partial.credit_move_id

            # In case we are in an onchange, line_ids is a NewId, not an integer. By using line_ids.ids we get the correct integer value.
            counterpart_line = counterpart_lines\
                                    .filtered(lambda line: \
                                                line.id not in self.line_ids.ids)

            if counterpart_line.date\
                and counterpart_line.date >= tax_term_date\
                and counterpart_line.date <= tax_term_date_end:
                _payment_moves_ids.append(counterpart_line.move_id.id)

        return _moves + self.env['account.move']\
                            .browse(_payment_moves_ids)