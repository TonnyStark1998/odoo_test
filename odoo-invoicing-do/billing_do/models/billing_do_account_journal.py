# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BillindDoAccountJournal(models.Model):
    _inherit = "account.journal"

    # Account Journal - Modified Fields
    refund_sequence_id = fields.Many2one(domain = "['&', ('company_id', '=', company_id), ('is_refund_sequence', '=', True)]")
    refund_sequence = fields.Boolean(readonly=True)