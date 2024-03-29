from odoo \
    import models, \
            fields, \
            exceptions, \
            api, \
            _
import logging as log

class BillingDoIrSequence(models.Model):
    _inherit = "ir.sequence"

    # Account Move - Modified Fields
    code = fields.Char(required=True,
                        default=_('<NOT_SET>'))

    # Ir Sequence - New Fields
    is_refund_sequence = fields.Boolean(default=False, 
                                            store=True, 
                                            tracking=True)
    
    # Ir Sequence Date Range - Overriden Methods
    def _next(self, sequence_date=None):
        if not self.use_date_range:
            return self._next_do()

        if not sequence_date:
            raise exceptions.ValidationError(_('Please select the invoice date first.'))

        seq_date = \
            self.env['ir.sequence.date_range']\
                .search([('sequence_id', '=', self.id),
                            ('date_from', '<=', sequence_date), 
                            ('date_to', '>=', sequence_date)])
        
        log.info('[KCS] Seq Date [1]: {}'.format(seq_date))
        log.info('[KCS] Self: {}'.format(self))
        log.info('[KCS] Sequence Date: {}'.format(sequence_date))
        
        seq_date = \
            seq_date.filtered(lambda seq: seq.number_next <= seq_date.number_last)

        log.info('[KCS] Seq Date [2]: {}'.format(seq_date))

        if not seq_date:
            raise exceptions.ValidationError(_('The sequence associated with this Journal ' +
                                               'does not contain any valid range or the sequence is over.'))

        if len(seq_date) > 1:
            seq_date = seq_date[0]

        return seq_date.with_context(ir_sequence_date_range=seq_date.date_from)._next()

    def next_by_id(self, sequence_date=None):
        sequence_date = self._context.get('ir_sequence_date')
        return super().next_by_id(sequence_date)
