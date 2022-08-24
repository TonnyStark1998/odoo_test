# -*- coding: utf-8 -*-

from odoo\
    import models, fields, _

class BillingDoAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Account Move Line - Related Fields
    invoice_user_id = fields.Many2one(related='move_id.invoice_user_id', 
                                        store=False, 
                                        Tracking=False)