# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class BillingDoAccountTax(models.Model):
    _inherit = "account.tax"

    tax_type = fields.Selection(selection=[
        ('CDT', 'CDT'),
        ('IPI', 'IPI'),
        ('ISC', 'ISC'),
        ('ISR', 'ISR'),
        ('ITBIS', 'ITBIS'),
        ('VEH', 'VEH'),
        ('Otro', 'Otro'),
        ('Propina', 'Propina')
    ], string="Tax Type", required=True, store=True, copy=True)