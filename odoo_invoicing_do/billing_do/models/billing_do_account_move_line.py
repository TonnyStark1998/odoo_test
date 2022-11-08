# -*- coding: utf-8 -*-

import re
import datetime as date
import logging as log

from odoo\
    import models, fields, _

class BillingDoAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        super(BillingDoAccountMoveLine, self).remove_move_reconcile()

        for line in self:
            self.env['auditlog.log']\
                .create({
                        'name': 'Move Line - Remove Reconcile: Line Id {}'
                                    .format(line.id),
                        'model_id': self.env['ir.model']
                                        .search([('model', '=', 'account.move.line')], limit = 1).id,
                        'res_id': line.id,
                        'user_id': self.env.user.id,
                        'method': 'write',
                        'log_type': 'fast'
                    })

            log.info("[KCS] AccountMoveLine.RemoveMoveReconcicle: User {} removed reconcile line id {}."
                        .format(self.env.user.login, line.id))
    
    # Account Move Line - Related Fields
    invoice_user_id = fields.Many2one(related='move_id.invoice_user_id', store=True)
