# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BillindDoAccountJournal(models.Model):
    _inherit = "account.journal"

    # Account Journal - New Fields
    is_tax_valuable = fields.Boolean(string='Is tax valuable?', copy=True, default=True)
    use_sequence = fields.Boolean(string='Use sequence?', copy=True, default=False)

    # Account Journal - Modified Fields
    refund_sequence_id = fields.Many2one(domain = "['&', ('company_id', '=', company_id), ('is_refund_sequence', '=', True)]")
    refund_sequence = fields.Boolean(readonly=True)
    type = fields.Selection(selection_add=[
            ('credit_debit_card', 'Credit/Debit Card'),
        ])
