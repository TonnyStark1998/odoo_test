# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class BillingDoIrSequence(models.Model):
    _inherit = "ir.sequence"

    # Account Move - Modified Fields
    code = fields.Char(required=True)

    # Ir Sequence - New Fields
    is_refund_sequence = fields.Boolean(default=False, store=True, tracking=True)