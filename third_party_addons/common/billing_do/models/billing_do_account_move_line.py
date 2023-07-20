# -*- coding: utf-8 -*-

import re
import datetime as date
import logging as log

from odoo\
    import models, fields, _, api

class BillingDoAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    exclude_from_invoice_tab = fields.Boolean(string='Exclude from Invoice Tab',
                                              compute='_compute_exclude_from_invoice_tab')

    account_internal_type = fields.Selection(related='account_type')

    # Account Move Line - Related Fields
    invoice_user_id = fields.Many2one(related='move_id.invoice_user_id', store=True)

    def remove_move_reconcile(self):
        super(BillingDoAccountMoveLine, self).remove_move_reconcile()
        
        move = self.env['account.move'].browse(self.env.context.get('move_id'))
        for line in self:
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
    
    @api.depends('display_type')
    def _compute_exclude_from_invoice_tab(self):
        for line in self:
            if line.display_type in ['product', 'line_section', 'line_note']:
                line.exclude_from_invoice_tab = False
            else:
                line.exclude_from_invoice_tab = True
