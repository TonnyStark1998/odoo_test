# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BillindDoAccountPayment(models.Model):
    _inherit = "account.payment"

    # Account Payment - Modified Fields
    journal_id = fields.Many2one(domain="[('type', 'in', ('bank', 'cash', 'credit_debit_card')), ('company_id', '=', company_id)]")
    writeoff_label = fields.Char(default=lambda self: self._default_get_writeoff_label())

    @api.model
    def _default_get_writeoff_label(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        if active_ids and active_model == 'account.move':
            invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
            return invoices[0].invoice_payment_ref or invoices[0].ref or invoices[0].name or invoices[0].ncf
        else:
            return 'Write-Off Label'