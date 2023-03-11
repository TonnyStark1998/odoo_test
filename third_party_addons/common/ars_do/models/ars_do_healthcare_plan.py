# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class ArsDoHealthcarePlan(models.Model):
    _name = 'ars.do.healthcare.plan'
    _description = 'Model representing a Healthcare Plan.'

    name = fields.Char(string='Healthcare Plan', 
                        size=20,
                        required=True)
    default_coverage = fields.Float(string='Default Coverage',
                                        required=False)

    healthcare_provider = fields.Many2one(string='Healthcare Provider', 
                                            comodel_name='res.partner',
                                            ondelete='restrict',
                                            domain=[('is_ars', '=', True)],
                                            readonly=True)

    healthcare_cards = fields.One2many(string='Healthcare Cards',
                                        comodel_name='ars.do.healthcare.card',
                                        inverse_name='healthcare_plan')