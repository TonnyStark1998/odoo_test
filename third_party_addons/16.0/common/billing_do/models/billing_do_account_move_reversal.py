# -*- coding: utf-8 -*-

from odoo\
    import models, fields, _

class BillingDoAccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    refund_method = fields.Selection(selection='_get_refund_method_selection')

    def _get_refund_method_selection(self):
        return [('refund', 'Partial Refund')]