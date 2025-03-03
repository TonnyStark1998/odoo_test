# -*- coding: utf-8 -*-
from odoo \
    import models, \
            fields, \
            api, \
            _

class BillingDoAccountJournal(models.Model):
    _inherit = "account.journal"

    # Account Journal - New Fields
    is_tax_valuable = fields.Boolean(string='Is tax valuable?',
                        copy=True,
                        default=True)
    use_sequence = fields.Boolean(string='Use sequence?',
                        copy=True,
                        default=False)

    type = fields.Selection(selection_add=[
                                ('credit_debit_card', 'Credit/Debit Card'),
                            ],
                            ondelete={'credit_debit_card': 'cascade'})
