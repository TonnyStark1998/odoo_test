# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import logging as log

class ArsDoHealthcareCard(models.Model):
    _name = 'ars.do.healthcare.card'
    _description = 'Model representing a Healthcare Card.'
    _rec_name = 'number'

    number = fields.Char(string='Card Number',
                            size=15,
                            required=True)
    default_card = fields.Boolean(string='Default Healthcare Cards?')
    expiry_date = fields.Date(string='Expiry Date')
    healthcare_provider = fields.Many2one(string='Healthcare Provider', 
                                            comodel_name='res.partner',
                                            ondelete='restrict',
                                            domain=['&', ('is_ars', '=', True),
                                                        ('healthcare_plans', '!=', False)],
                                            required=True)

    healthcare_plan = fields.Many2one(string='Healthcare Plan',
                                        comodel_name='ars.do.healthcare.plan',
                                        ondelete='restrict',
                                        domain=[('healthcare_provider', '=', -1)],
                                        required=True)

    healthcare_patient = fields.Many2one(string='Healthcare Patient',
                                            comodel_name='res.partner')
    
    @api.onchange('healthcare_provider')
    def _onchange_healthcare_provider(self):
        self.ensure_one() 
        if self.healthcare_provider:
            return {
                'domain': {
                    'healthcare_plan': [('healthcare_provider', '=', self.healthcare_provider.id)]
                }
            }

    @api.onchange('default_card')
    def _onchange_default_card(self):
        self.ensure_one()
        has_default_card = self.env['ars.do.healthcare.card']\
                                .search_count(args=['&', ('default_card', '=',True), 
                                                            ('healthcare_patient', '=', self.healthcare_patient._origin.id)]) > 0
        if has_default_card and self.default_card:
            self.default_card = False
            return {
                'warning': {
                    'title': _('User error!'),
                    'message': _('There is already a default card for this patient. Deactivate it first before marking another one as default.')
                }
            }

    # Model Methods
    def create(self, values):
        for card in values:
            has_default_card = self.env['ars.do.healthcare.card']\
                                .search_count(args=[('default_card', '=',True), 
                                                    ('healthcare_patient', '=', card['healthcare_patient'])]) > 0
            if 'default_card' in card:
                if not has_default_card:
                    card['default_card'] = True
        super(ArsDoHealthcareCard,self).create(values)
