# -*- coding: utf-8 -*-

from odoo\
    import models, fields, api, _

class BillingDoNcfType(models.Model):
    _name = 'billing.do.ncf.type'
    _description = 'Billing DO NCF Type'

    serie = fields.Char(string='Serie', 
                         required=True)
    code = fields.Char(string='Code', 
                       required=True)
    type = fields.Char(string='Type',
                       compute='_compute_type')
    name = fields.Char(string='Name', 
                       required=True)
    display_name = fields.Char(string='Display Name', 
                               required=True)
    sequence = fields.Many2one(comodel_name='ir.sequence',
                               string='Sequences',
                               ondelete='cascade')
    is_sale_usable = fields.Boolean(string='Can be use in sales?')
    is_purchase_usable = fields.Boolean(string='Can be use in purchases?')
    
    @api.depends('serie', 'code')
    def _compute_type(self):
        for ncf_type in self:
            ncf_type.type = '{}{}'.format(ncf_type.serie, ncf_type.code)

