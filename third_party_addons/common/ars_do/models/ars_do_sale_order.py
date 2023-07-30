# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging as log

class ArsDoSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Model representing the Healthcare Sale Order.'

    healthcare_invoice = \
        fields.Selection(selection=[('healthcare_invoice', 'Insurance'),
                            ('not_healthcare_invoice', 'Private')],
            string='Healthcare Invoice')

    # Changes methods
    @api.onchange('healthcare_invoice')
    def _onchange_healthcare_invoice(self):
        self.ensure_one()
        self.partner_id = None

        if self.healthcare_invoice == 'healthcare_invoice':
            return {
                'domain': {
                        'partner_id': [('is_patient', '=', True), ('healthcare_cards_count', '>', 0)]
                }
            }

        return {
            'domain': {
                'partner_id': []
            }
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if not self.healthcare_invoice and self.partner_id:
            self.partner_id = False
            return { 
                    'warning': {
                        'title': _('User error!'),
                        'message': _('You must indicate if this is a Healthcare or Regular sale before selecting the Customer.')
                    }
            }

    # Contraints methods
    @api.constrains('healthcare_invoice')
    def _constrain_healthcare_invoice(self):
        for sale_order in self:
            if not sale_order.healthcare_invoice:
                raise exceptions.ValidationError(_('You must indicate if this is a Healthcare or Regular sale.'))

    def _prepare_invoice(self):
        invoice = super()._prepare_invoice()
        invoice.update({
            'healthcare_invoice': self.healthcare_invoice,
            'healthcare_card': self.partner_invoice_id
                                    .healthcare_cards
                                    .filtered(lambda hc: hc.default_card == True)
                                    .id,
            'created_from_sale': True
        })
        return invoice