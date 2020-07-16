from odoo import models, fields, api, exceptions

class BillingDoIrSequence(models.Model):
    _inherit = "ir.sequence"

    # Ir Sequence - New Fields
    is_refund_sequence = fields.Boolean(default=False, store=True, tracking=True)