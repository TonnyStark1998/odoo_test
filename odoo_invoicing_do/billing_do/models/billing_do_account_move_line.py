# -*- coding: utf-8 -*-

import re
import datetime as date
import logging as log

from odoo\
    import models, fields, _

class BillingDoAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        # TODO: Add log to see which user execute this action
        super(BillingDoAccountMoveLine, self).remove_move_reconcile()
        for line in self:
            log.info("[KCS] AccountMoveLine.RemoveMoveReconcicle: User {} removed reconcile {} from move id {}"
                        .format(self.env.user.login, line.id, line.move_id.id))
    
    # Account Move Line - Related Fields
    invoice_user_id = fields.Many2one(related='move_id.invoice_user_id', store=True)
