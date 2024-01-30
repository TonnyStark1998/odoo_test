from odoo \
    import models, \
            fields, \
            api, \
            _

class BillingDoIrSequenceDateRange(models.Model):
    _inherit = "ir.sequence.date_range"

    # Ir Sequence Date Range - New Fields
    number_last = fields.Integer(string='Last Number', 
                                required=True, 
                                help="Last number of this sequence",
                                default=0)
    
    sequence_count_left = fields.Integer(string='Sequence Count Left',
                                         compute='_compute_sequence_count_left',
                                         store=True,
                                         default=10)
    
    @api.depends('number_next_actual', 'number_last')
    def _compute_sequence_count_left(self):
        for sequence in self:
            sequence.sequence_count_left = \
                sequence.number_last - sequence.number_next_actual
