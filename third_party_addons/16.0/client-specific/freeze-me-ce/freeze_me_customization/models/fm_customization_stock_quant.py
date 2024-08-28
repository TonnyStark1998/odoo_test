# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class FreezeMeCustomizationStockQuant(models.Model):
    _inherit = 'stock.quant'

    product_name = fields.Char(string='Product Name',
        related='product_id.name')
    
    available_quantity = fields.Float(search='_search_on_available_quantity')

    def _search_on_available_quantity(self, operator, value):
        if operator not in ['=', '!=', '<', '>'] or not isinstance(value, int):
            raise UserError(_('Operation not supported'))
        
        domain_operator = 'not in'
        if operator == '=':
            stock_quants = self.search([]).filtered(lambda sq: sq.available_quantity == value)
            domain_operator = 'in'
        elif operator == '!=':
            stock_quants = self.search([]).filtered(lambda sq: sq.available_quantity != value)
            domain_operator = 'in'
        elif operator == '>' or operator == '<':
            stock_quants = self.search([]).filtered(lambda sq: sq.available_quantity > value)

        if operator == '>':
            domain_operator = 'in'

        return [('id', domain_operator, stock_quants.ids)]

