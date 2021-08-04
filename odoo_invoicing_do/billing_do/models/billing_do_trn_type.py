# -*- coding: utf-8 -*-

from odoo import models,\
                    fields,\
                    exceptions,\
                    api,\
                    _

class BillingDoTrnType(models.Model):
    _name = 'billing.do.trn.type'
    _description = 'Billing DO - TRN Type'

    # TRN Type - New Fields
    name = fields.Char(string='Name',
                        required=True)
    description = fields.Text(string='Description')
    code_length = fields.Integer(string='Code Length',
                                    required=True,
                                    default=1)
    code = fields.Char(string='Code',
                        required=True)
    regular_expression = fields.Char(string='Regular Expression',
                                        required=True)
    active = fields.Boolean(string='Active',
                                default=False)
    min_length = fields.Integer(string='Minimun Length',
                                    required=True)
    max_length = fields.Integer(string='Maximun Length',
                                    required=True)

    # TRN Type - onchange Fields Functions
    @api.onchange('regular_expression')
    def _onchange_regular_expression(self):
        return True
    
    # TRN Type - Contraints Fields Functions
    @api.constrains('regular_expression')
    def _check_regular_expression(self):
        return True