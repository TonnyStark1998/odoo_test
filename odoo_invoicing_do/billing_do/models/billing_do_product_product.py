# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BillindDoProductProduct(models.Model):
    _inherit = "product.template"

    # Account Journal - Modified Fields
    company_id = fields.Many2one(default=lambda self: self.env.company,
                                    readonly=True)
