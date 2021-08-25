from odoo \
    import models, \
            fields, \
            api, \
            exceptions, \
            _

class BillingDoIrSequence(models.Model):
    _inherit = "ir.sequence"

    # Account Move - Modified Fields
    code = fields.Char(required=True,
                        default=_('<NOT_SET>'))

    # Ir Sequence - New Fields
    is_refund_sequence = fields.Boolean(default=False, 
                                            store=True, 
                                            tracking=True)