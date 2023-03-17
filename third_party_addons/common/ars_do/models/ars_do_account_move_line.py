# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ArsDoAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Model representing a Invoice Line.'

    coverage = fields.Float(string='Coverage (%)', 
                                digits=(3,2))
    
    healthcare_invoice = fields.Selection(string='Healthcare Invoice',
                                            related='move_id.healthcare_invoice')

    @api.onchange('coverage')
    def _onchange_coverage(self):
        for line in self:
            if line.move_id.healthcare_invoice == 'healthcare_invoice':
                if not line.move_id.is_invoice(include_receipts=True):
                    continue

                line.update(line._get_price_total_and_subtotal())
                line.update(line._get_fields_onchange_subtotal())
            elif line.move_id.healthcare_invoice == 'not_healthcare_invoice':
                if line.coverage > 0.0:
                    line.coverage = 0.0
                    return {
                        'warning': {
                            'title': _('User error!'),
                            'message': _('This invoice is not a healthcare invoice, you can\'t apply any coverage value.')
                        }
                    }
    
    def _get_price_total_and_subtotal(self, 
                                        price_unit=None, 
                                        quantity=None, 
                                        discount=None, 
                                        currency=None, 
                                        product=None, 
                                        partner=None, 
                                        taxes=None, 
                                        move_type=None):
        self.ensure_one()
        price_total_and_subtotal = super(ArsDoAccountMoveLine, self)._get_price_total_and_subtotal(price_unit, 
                                                                                                    quantity, 
                                                                                                    discount, 
                                                                                                    currency, 
                                                                                                    product, 
                                                                                                    partner, 
                                                                                                    taxes, 
                                                                                                    move_type)
        if self.coverage > 0:
            price_total_and_subtotal['price_subtotal'] = \
                price_total_and_subtotal['price_subtotal'] * (1 - (self.coverage / 100))

        price_total_and_subtotal['coverage'] = self.coverage

        return price_total_and_subtotal