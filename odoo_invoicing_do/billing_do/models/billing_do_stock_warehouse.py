from odoo import models, fields, api, exceptions
from . import billing_do_utils as doutils
import logging as log

class BillingDoStockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        self.env['res.partner'].browse(vals['partner_id']).write({
            'company_id': vals['company_id']
        })
        warehouse = super(BillingDoStockWarehouse, self).create(vals)
        return warehouse