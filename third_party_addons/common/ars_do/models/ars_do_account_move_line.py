# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging as log
from odoo.tools import frozendict

class ArsDoAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Model representing a Invoice Line.'

    coverage = fields.Float(string='Coverage (%)', 
                                digits=(3,2),
                                tracking=True)
    
    healthcare_invoice = fields.Selection(string='Healthcare Invoice',
                                            related='move_id.healthcare_invoice')

    @api.onchange('coverage')
    def _onchange_coverage(self):
        for line in self:
            if line.move_id.healthcare_invoice == 'healthcare_invoice':
                if not line.move_id.is_invoice(include_receipts=True):
                    continue

                line._compute_totals()
            elif line.move_id.healthcare_invoice == 'not_healthcare_invoice':
                if line.coverage > 0.0:
                    line.coverage = 0.0
                    return {
                        'warning': {
                            'title': _('User error!'),
                            'message': _('This invoice is not a healthcare invoice, you can\'t apply any coverage value.')
                        }
                    }
    
    @api.depends('coverage')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))

            if line.move_id.healthcare_invoice == 'healthcare_invoice':
                line_discount_price_unit = line_discount_price_unit * (1 - (line.coverage / 100.0))

            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']
                line.price_total = taxes_res['total_included']
            else:
                line.price_total = line.price_subtotal = subtotal

    @api.depends('coverage')
    def _compute_all_tax(self):
        for line in self:
            sign = line.move_id.direction_sign
            if line.display_type == 'tax':
                line.compute_all_tax = {}
                line.compute_all_tax_dirty = False
                continue
            if line.display_type == 'product' and line.move_id.is_invoice(True):
                amount_currency = sign * line.price_unit * (1 - line.discount / 100)

                if line.move_id.healthcare_invoice == 'healthcare_invoice':
                    amount_currency = amount_currency * (1 - (line.coverage / 100.0))

                handle_price_include = True
                quantity = line.quantity
            else:
                amount_currency = line.amount_currency
                handle_price_include = False
                quantity = 1
            compute_all_currency = line.tax_ids.compute_all(
                amount_currency,
                currency=line.currency_id,
                quantity=quantity,
                product=line.product_id,
                partner=line.move_id.partner_id or line.partner_id,
                is_refund=line.is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=line.move_id.always_tax_exigible,
                fixed_multiplicator=sign,
            )
            rate = line.amount_currency / line.balance if line.balance else 1
            line.compute_all_tax_dirty = True
            line.compute_all_tax = {
                frozendict({
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'group_tax_id': tax['group'] and tax['group'].id or False,
                    'account_id': tax['account_id'] or line.account_id.id,
                    'currency_id': line.currency_id.id,
                    'analytic_distribution': (tax['analytic'] or not tax['use_in_tax_closing']) and line.analytic_distribution,
                    'tax_ids': [(6, 0, tax['tax_ids'])],
                    'tax_tag_ids': [(6, 0, tax['tag_ids'])],
                    'partner_id': line.move_id.partner_id.id or line.partner_id.id,
                    'move_id': line.move_id.id,
                }): {
                    'name': tax['name'],
                    'balance': tax['amount'] / rate,
                    'amount_currency': tax['amount'],
                    'tax_base_amount': tax['base'] / rate * (-1 if line.tax_tag_invert else 1),
                }
                for tax in compute_all_currency['taxes']
                if tax['amount']
            }
            if not line.tax_repartition_line_id:
                line.compute_all_tax[frozendict({'id': line.id})] = {
                    'tax_tag_ids': [(6, 0, compute_all_currency['base_tags'])],
                }

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        is_invoice = self.move_id.is_invoice(include_receipts=True)
        sign = -1 if self.move_id.is_inbound(include_receipts=True) else 1

        price_unit = self.price_unit if is_invoice else self.amount_currency
        price_subtotal = sign * self.amount_currency

        log.info('[KCS][After] Line Id: {}; Price Unit: {}; Price Subtotal: {}'
                .format(self.id, price_unit, price_subtotal))

        if self.move_id.healthcare_invoice == 'healthcare_invoice':
            price_unit = price_unit * (1 - (self.coverage / 100.0))
            price_subtotal = price_subtotal * (1 - (self.coverage / 100.0))

        log.info('[KCS][After] Line Id: {}; Price Unit: {}; Price Subtotal: {}'
                .format(self.id, price_unit, price_subtotal))

        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.partner_id,
            currency=self.currency_id,
            product=self.product_id,
            taxes=self.tax_ids,
            price_unit=price_unit,
            quantity=self.quantity if is_invoice else 1.0,
            discount=self.discount if is_invoice else 0.0,
            account=self.account_id,
            analytic_distribution=self.analytic_distribution,
            price_subtotal=price_subtotal,
            is_refund=self.is_refund,
            rate=(abs(self.amount_currency) / abs(self.balance)) if self.balance else 1.0
        )

    def _convert_to_tax_line_dict(self):
        self.ensure_one()
        sign = -1 if self.move_id.is_inbound(include_receipts=True) else 1

        tax_amount = sign * self.amount_currency

        log.info('[KCS][Before] Line Id: {}; Tax Amount: {}'
                .format(self.id, tax_amount))

        if self.move_id.healthcare_invoice == 'healthcare_invoice':
            tax_amount = tax_amount * (1 - (self.coverage / 100.0))

        log.info('[KCS][After] Line Id: {}; Tax Amount: {}'
                .format(self.id, tax_amount))

        return self.env['account.tax']._convert_to_tax_line_dict(
            self,
            partner=self.partner_id,
            currency=self.currency_id,
            taxes=self.tax_ids,
            tax_tags=self.tax_tag_ids,
            tax_repartition_line=self.tax_repartition_line_id,
            group_tax=self.group_tax_id,
            account=self.account_id,
            analytic_distribution=self.analytic_distribution,
            tax_amount=tax_amount,
        )