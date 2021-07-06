# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

import datetime
import logging as log

class BillingDoTaxReportItem606(models.Model):
    _name = 'billing.do.tax.report.item.606'
    _description = 'Billing DO Tax Report 606'
    _inherit = 'billing.do.tax.report.item.common'

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

    def generate_items(self, search_domain_common, tax_report):
        moves = self.env['account.move'].search(search_domain_common +
                                                    [('type', 'in', ['in_invoice', 'in_refund'])])
        
        for move in moves:
            tax_report_item = super(BillingDoTaxReportItem606, self)\
                                .generate_item(move, tax_report)

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
            _move_lines = self._get_move_lines_and_payment_lines(move, _reconciled_values)

            _payment_type = False
            _tax_balance_multiplicator = -1 if move.is_inbound(True) else 1

            tax_report_item['consumable_amount'] = 0.0
            tax_report_item['service_amount'] = 0.0
            tax_report_item['total_amount'] = 0.0
            tax_report_item['tax_amount'] = 0.0
            tax_report_item['other_taxes_amount'] = 0.0
            tax_report_item['legaltip_amount'] = 0.0

            for move_line in _move_lines:
                if move_line.account_internal_type in ['receivable']\
                    and move_line.payment_id:
                    _payment_type = self._get_payment_type(move_line.journal_id)

                if move_line.account_id.withholding_tax_type in ["RET-ITBIS-606"]:
                    tax_report_item['held_amount_itbis'] += \
                        move_line.credit + move_line.debit
                elif move_line.account_id.withholding_tax_type in ["RET-ISR-606"]:
                    tax_report_item['held_amount_isr'] += \
                        move_line.credit + move_line.debit
                
                if not move_line.exclude_from_invoice_tab:
                    # Calculate the consumable and services amounts
                    unit_price = move_line.price_subtotal
                    if move_line.currency_id:
                        unit_price = move_line.currency_id\
                                                ._convert(unit_price, 
                                                            self.env.company.currency_id, 
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
                    tax_amount = _tax_balance_multiplicator * move_line.balance

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

            tax_report_item['payment_type'] = '04'
            if move.invoice_payment_state in ['paid']:
                tax_report_item['payment_type'] = _payment_type

                if tax_report_item['held_amount_itbis'] > 0 \
                        or tax_report_item['held_amount_isr'] > 0:
                    
                    _last_payment_date = self._get_payment_last_date(_reconciled_values)

                    tax_report_item['date_payment_month'] = _last_payment_date.strftime('%Y%m')
                    tax_report_item['date_payment_day'] = _last_payment_date.strftime('%d')

            self.create(tax_report_item)

        return len(moves)