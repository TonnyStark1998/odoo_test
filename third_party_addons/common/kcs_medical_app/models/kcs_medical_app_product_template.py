# -*- coding: utf-8 -*-

import logging as log
from odoo import models, fields, api

class PatientBudgetProduct(models.Model):
    _inherit = 'product.product'

    # Patient Budget Product - New Fields
    patient_evolution_type = fields.Selection(selection=[
                                                            ('plastic_surgery', 'Platic Surgery'),
                                                            ('stetic_surgery', 'Stetic Surgery'),
                                                        ], 
                                                string='Patient Evolution Product Type', 
                                                required=False, 
                                                store=True, 
                                                copy=False,
                                                default='plastic_surgery')