# -*- coding: utf-8 -*-
import logging as log

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

    def action_draft(self):
        super(BillindDoAccountPayment, self).action_draft()

        self.env['auditlog.log'].create({
            'name': 'Payment set to draft'
                        .format(self.env.user.login, self.id),
            'model_id': self.env['ir.model']
                            .search([('model', '=', 'account.payment')], limit = 1).id,
            'res_id': self.id,
            'user_id': self.env.user.id,
            'method': 'write',
            'log_type': 'fast'
        })

        log.info("[KCS] AccountPayment.ActionDraft: User {} revert the payment {} to draft state."
                    .format(self.env.user.login, self.id))

    def _compute_journal_domain_and_types(self):
        journal_types_and_domain = super(BillindDoAccountPayment, self)._compute_journal_domain_and_types()
        journal_types = journal_types_and_domain['journal_types']
        journal_types.add('credit_debit_card')
        journal_types_and_domain.update({
            'domain' : journal_types_and_domain['domain'],
            'journal_types' : journal_types
        })
        log.info('[KCS] Journal Types & Domain: {}'.format(journal_types_and_domain))
        return journal_types_and_domain