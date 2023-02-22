# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import logging as log

class ArsDoHealthcareMedicine(models.Model):
    _inherit = 'product.product'
    _description = 'Model representing a Healthcare Medicine.'

    is_medicine = fields.Boolean(string='Is a medicine?')

