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
        
        move = self.env['account.move'].browse(self.env.context.get('move_id'))
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

            self.env['mail.message'].create({
                'subject': _('Payment unreconciled.'),
                'body': _("<p style='margin:0px; font-size:13px; font-family:'Lucida Grande', Helvetica, Verdana, Arial, sans-serif'><strong>Payment with line id</strong> {} - {} <strong>has been unreconciled.</strong> </p>")
                            .format(line.id, line.name),
                'model': 'account.move',
                'res_id': move.id,
                'record_name': move.name,
                'email_from': self.env.user.login,
                'author_id': self.env.user.partner_id.id,
                'message_type': 'comment',
                'subtype_id': 2
            })

            log.info("[KCS] AccountMoveLine.RemoveMoveReconcicle: User {} removed reconcile line id {}."
                        .format(self.env.user.login, line.id))
    
    # Account Move Line - Related Fields
    invoice_user_id = fields.Many2one(related='move_id.invoice_user_id', store=True)
