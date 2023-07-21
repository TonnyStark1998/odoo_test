# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ArsDoAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Model representing a Invoice Line.'

    coverage = fields.Float(string='Coverage (%)', 
                                digits=(3,2),
                                tracking=True)
    
    healthcare_invoice = fields.Selection(string='Healthcare Invoice',
                                            related='move_id.healthcare_invoice')

    @api.onchange('coverage')
    def _onchange_coverage(self):
        for line in self:
            if line.move_id.healthcare_invoice == 'healthcare_invoice':
                if not line.move_id.is_invoice(include_receipts=True):
                    continue

                line._compute_totals()
            elif line.move_id.healthcare_invoice == 'not_healthcare_invoice':
                if line.coverage > 0.0:
                    line.coverage = 0.0
                    return {
                        'warning': {
                            'title': _('User error!'),
                            'message': _('This invoice is not a healthcare invoice, you can\'t apply any coverage value.')
                        }
                    }
    
    @api.depends('coverage')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))

            if line.move_id.healthcare_invoice == 'healthcare_invoice':
                line_discount_price_unit = line_discount_price_unit * (1 - (line.coverage / 100.0))

            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']
                line.price_total = taxes_res['total_included']
            else:
                line.price_total = line.price_subtotal = subtotal

    # def _get_price_total_and_subtotal(self, 
    #                                     price_unit=None, 
    #                                     quantity=None, 
    #                                     discount=None, 
    #                                     currency=None, 
    #                                     product=None, 
    #                                     partner=None, 
    #                                     taxes=None, 
    #                                     move_type=None):
    #     self.ensure_one()
    #     price_total_and_subtotal = super(ArsDoAccountMoveLine, self)._get_price_total_and_subtotal(price_unit, 
    #                                                                                                 quantity, 
    #                                                                                                 discount, 
    #                                                                                                 currency, 
    #                                                                                                 product, 
    #                                                                                                 partner, 
    #                                                                                                 taxes, 
    #                                                                                                 move_type)
    #     if self.coverage > 0:
    #         price_total_and_subtotal['price_subtotal'] = \
    #             price_total_and_subtotal['price_subtotal'] * (1 - (self.coverage / 100))

    #     price_total_and_subtotal['coverage'] = self.coverage

    #     return price_total_and_subtotal