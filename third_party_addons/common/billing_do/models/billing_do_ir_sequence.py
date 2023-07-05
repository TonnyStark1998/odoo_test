from odoo \
    import models, \
            fields

class BillingDoIrSequence(models.Model):
    _inherit = "ir.sequence"

    ncf_type = fields.Many2one(comodel_name='billing.do.ncf.type',
                               string='NCF Type',
                               ondelete='restrict')
    
class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    number_last = fields.Integer(string='Last Number', 
                                 required=True, 
                                 help="Last number of this sequence")