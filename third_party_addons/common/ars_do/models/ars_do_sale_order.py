# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging as log

class ArsDoSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Model representing the Healthcare Sale Order.'

    healthcare_invoice = fields.Selection(selection=[('healthcare_invoice', 'Insurance'),
                                                        ('not_healthcare_invoice', 'Private')],
                                            string='Healthcare Invoice')

    # Changes methods
    @api.onchange('healthcare_invoice')
    def _onchange_healthcare_invoice(self):
        self.ensure_one()
        self.partner_id = None
        self.healthcare_card = None

        if self.healthcare_invoice == 'healthcare_invoice':
            return {
                'domain': {
                        'partner_id': [('is_patient', '=', True)]
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

        if self.healthcare_invoice == 'healthcare_invoice':
            if self.partner_id:
                if not self.partner_id.is_patient:
                    self.partner_id = False
                else:
                    self.healthcare_card = self.partner_id.healthcare_cards\
                                                            .filtered(lambda self: self.default_card == True)
                return {
                        'domain': {
                            'partner_id': [('is_patient', '=', True)]
                        }
                    }

    # Contraints methods
    @api.constrains('healthcare_invoice')
    def _constrain_healthcare_invoice(self):
        for sale_order in self:
            if not sale_order.healthcare_invoice:
                raise exceptions.ValidationError(_('You must indicate if this is a Healthcare or Regular sale.'))

    # Actions Methods
    def action_create_healthcare_invoice(self):
        log.info('[KCS] Self: {}'.format(self))
        log.info('[KCS] Partner_Id: {}'.format(self.partner_id))
        log.info('[KCS] Healthcare Cards: {}'.format(self.partner_id.healthcare_cards))
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "domain": [],
            "context": {
                'default_move_type': 'out_invoice',
                'default_healthcare_invoice': self.healthcare_invoice,
                'default_partner_id': self.partner_id.id,
                'default_healthcare_card': self.partner_id.healthcare_cards
                                                .filtered(lambda self: self.default_card == True)
                                                .id,
                'default_created_from_sale': True
            }
        }