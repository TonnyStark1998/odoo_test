# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class BillingDoAccountAccount(models.Model):
    _inherit = "account.account"

    withholding_tax_type = fields.Selection(selection=[
        ('RET-ITBIS-606', 'Retencion ITBIS 606'),
        ('RET-ITBIS-607', 'Retencion ITBIS 607'),
        ('RET-ISR-606', 'Retencion ISR 606'),
        ('RET-ISR-607', 'Retencion ISR 607'),
    ], string='Withholding Tax Type', required=False, store=True, copy=True)