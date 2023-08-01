# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging as log
from odoo.exceptions import UserError

class ArsDoAccountTax(models.Model):
    _inherit = 'account.tax'
    _description = 'Model representing a Account Tax.'

    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        tax_totals = \
            super()._prepare_tax_totals(base_lines, currency, tax_lines)
        
        