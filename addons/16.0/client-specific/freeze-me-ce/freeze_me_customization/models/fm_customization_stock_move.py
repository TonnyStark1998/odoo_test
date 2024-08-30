# -*- coding: utf-8 -*-

import logging as log

from odoo\
    import models, fields, api, _
from odoo.exceptions import UserError

class FreezeMeCustomizationStockMove(models.Model):
    _inherit = "stock.move"
    _description = """
        Agrega ciertas modificaciones al modelo original de la información requerida por la empresa Freeze Me.
    """

    bulk_creation = fields.Boolean(string='Bulk Creation',
        default=False)

    def _set_product_qty(self):
        """ The meaning of product_qty field changed lately and is now a functional field computing the quantity
        in the default product UoM. This code has been added to raise an error if a write is made given a value
        for `product_qty`, where the same write should set the `product_uom_qty` field instead, in order to
        detect errors. """
        for move in self:
            if not move.bulk_creation:
                raise UserError(_('The requested operation cannot be processed because of a programming error setting the `product_qty` field instead of the `product_uom_qty`.'))