# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class ArsDoResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Model representing the Healthcare Provider.'
    _order = 'name asc'

    # Basic Fields
    is_ars = fields.Boolean(string='Is ARS?',
                                default=False)
    healthcare_plans_count = fields.Integer(string='Healthcare Plans Count',
                                                compute='_compute_healthcare_counts',
                                                store=True)
    is_patient = fields.Boolean(string='Is Patient?',
                                    	default=False)
    healthcare_cards_count = fields.Integer(string='Healthcare Cards Count',
                                                compute='_compute_healthcare_counts',
                                                store=True)

    # Relational Fields
    healthcare_cards = fields.One2many(string='Healthcare Cards',
                                        comodel_name='ars.do.healthcare.card',
                                        inverse_name='healthcare_patient')
    healthcare_plans = fields.One2many(string='Healthcare Plans',
                                        comodel_name='ars.do.healthcare.plan',
                                        inverse_name='healthcare_provider')
    medical_records = fields.One2many(string='Medical Records',
                                        comodel_name='ars.do.healthcare.medical.record',
                                        inverse_name='healthcare_patient')

    # Compute Functions
    @api.depends('healthcare_plans', 'healthcare_cards')
    def _compute_healthcare_counts(self):
        for partner in self:
            partner.healthcare_plans_count = 1 #len(partner.healthcare_plans)
            partner.healthcare_cards_count = 2 #len(partner.healthcare_cards)
