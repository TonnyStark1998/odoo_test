# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

import logging as log

class BillingDoTaxReportItemCommon(models.AbstractModel):
    _name = 'billing.do.tax.report.item.common'
    _description = 'Billing DO - Tax Report Common'
    _inherit = 'billing.do.tax.report.item'

    currency_id = fields.Many2one(string='Currency',
                                    comodel_name='res.currency')

    held_amount_itbis = fields.Monetary(string='ITBIS Held Amount',
                                            default=0.00)
    held_amount_isr = fields.Monetary(string='ISR Held Amount',
                                            default=0.00)
    isc_amount = fields.Monetary(string='ISC Amount',
                                    default=0.00)
    
    def generate_item(self, move, tax_report):
        tax_report_item = super(BillingDoTaxReportItemCommon, self)\
                                .generate_item(move, tax_report)
        
        tax_report_item.update({
                        'held_amount_itbis': 0.00,
                        'held_amount_isr': 0.00,
                        'isc_amount': 0.00
                    })

        return tax_report_item

    def generate_items(self, tax_report, tax_term_date):
        _moves = super(BillingDoTaxReportItemCommon, self)\
                    .generate_items(tax_report, tax_term_date)
        
        for move in _moves:
            tax_report_item = self.generate_item(move, tax_report)
        
        self.create(tax_report_item)

        return _moves
    
    def _get_payment_type(self, journal):
        if journal.type in ['cash']:
            return '01'
        elif journal.type in ['bank']:
            return '02'
        elif journal.type in ['credit_debit_card']:
            return '03'
        else:
            return '07'
    
    def _get_payment_lines(self, reconciled_values):
        move_ids = [move_line['move_id'] \
                        for move_line in reconciled_values]

        _payment_move_lines = self.env['account.move.line']\
                                    .search(domain=[('move_id', 'in', move_ids)])

        return _payment_move_lines

    def _get_payment_last_date(self, reconciled_values):
        _last_payment_date = False

        if reconciled_values:
            _last_payment_date = max([payment['date'] 
                                        for payment in reconciled_values 
                                        if 'date' in payment
                                            and payment['date']])

        return _last_payment_date

    def _get_move_line_currency(self, move_line):
        return move_line.currency_id or move_line.company_currency_id

    def _convert_amount_to_dop(self, currency, amount, date, company):
        if self._is_dop_currency(currency):
            return amount
        
        return currency._convert(amount, 
                                    self.env['res.currency']
                                        .search([('name', '=', 'DOP')]), 
                                    company, 
                                    date, 
                                    True
                                )

    def _is_dop_currency(self, currency):
        return self.env['res.currency']\
                    .search([('name', '=', currency.name)])\
                    .is_dop_currency()