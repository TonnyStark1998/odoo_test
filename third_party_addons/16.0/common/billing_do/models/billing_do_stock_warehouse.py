# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging as log

class BillingDoStockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        self.env['res.partner'].browse(vals['partner_id']).write({
            'company_id': self.env.company.id
        })
        warehouse = super(BillingDoStockWarehouse, self).create(vals)
        return warehouse
