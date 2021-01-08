# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BillindDoAccountPayment(models.Model):
    _inherit = "account.payment"

    # Account Payment - Modified Fields
    journal_id = fields.Many2one(domain="[('type', 'in', ('bank', 'cash', 'credit_debit_card')), ('company_id', '=', company_id)]")