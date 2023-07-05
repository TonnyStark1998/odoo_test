# -*- coding: utf-8 -*-
import logging as log

from odoo import models, fields, api, _

class BillindDoAccountPayment(models.TransientModel):
    _name = 'account.payment.register'
    _inherit = 'account.payment.register'

    # Account Payment Register - Modified Fields
    journal_id = fields.Many2one(domain="[('type', 'in', ('bank', 'cash', 'credit_debit_card')),\
                                                            ('company_id', '=', company_id)]")