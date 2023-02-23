# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging as log

class ArsDoAccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Model representing a Account Move.'

    healthcare_invoice = fields.Selection(string='Healthcare Invoice',
                                            selection=[
                                                ('healthcare_invoice', 'Healthcare'),
                                                ('not_healthcare_invoice', 'Regular')
                                            ])

    healthcare_card = fields.Many2one(string='Healthcare Card',
                                        comodel_name='ars.do.healthcare.card',
                                        readonly=True)
    healthcare_provider = fields.Char(related='healthcare_card.healthcare_plan.healthcare_provider.name',
                                        store=True,
                                        readonly=True)
    healthcare_plan = fields.Char(related='healthcare_card.healthcare_plan.name',
                                    store=True,
                                    readonly=True)
    healthcare_authorization_number = fields.Char(string='Healthcare Authorization Number',
                                                    size=20)

    # Changes methods
    @api.onchange('healthcare_invoice')
    def _onchange_healthcare_invoice(self):
        self.ensure_one()
        self.partner_id = None
        self.healthcare_card = None
        if self.line_ids:
            for line in self.line_ids:
                line.coverage = 0.0
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
        if self.type in ['out_invoice', 'out_refund']:
            if not self.healthcare_invoice and self.partner_id:
                self.partner_id = False
                return { 
                        'warning': {
                            'title': _('User error!'),
                            'message': (_('You must indicate if this is a Healthcare or Regular invoice before selecting the Customer.'))
                        }
                }

            if self.healthcare_invoice == 'healthcare_invoice':
                if self.partner_id:
                    if not self.partner_id.is_patient:
                        self.partner_id = False
                        return {
                            'domain': {
                                    'partner_id': [('is_patient', '=', True)]
                            }
                        }

                    self.healthcare_card = self.partner_id.healthcare_cards\
                                                            .filtered(lambda self: self.default_card == True)

    # Contraints methods
    @api.constrains('healthcare_invoice')
    def _constrain_healthcare_invoice(self):
        for move in self:
            if move.type in ['out_invoice', 'out_refund'] and not move.healthcare_invoice:
                raise exceptions.ValidationError(_('You must indicate if this is a Healthcare or Regular invoice.'))