# -*- coding: utf-8 -*-
from odoo import models

class MedicalAppSaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Overrides to model Sale Order"

    def remove_narration_from_invoice(self, invoices):
        for invoice in invoices:
            invoice.write({
                'narration': ''
            })