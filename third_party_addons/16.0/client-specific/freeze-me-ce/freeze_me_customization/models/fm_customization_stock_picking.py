# -*- coding: utf-8 -*-

import logging

from odoo\
    import models, fields, api

class FreezeMeCustomizationStockPicking(models.Model):
    _inherit = "stock.picking"
    _description = """
        Agrega ciertas modificaciones al modelo original de la información requerida por la empresa Freeze Me.
    """

    partner_id = fields.Many2one(required=True)

    stock_picking_bulk_id = fields.Many2one('freeze.me.customization.stock.picking.bulk', 
        string='Stock Picking Bulk Id', 
        ondelete='restrict')
    
    kanban_state = fields.Char(string='Kanban State',
        default='draft')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.picking_type_id.code in ['incoming']:
            self.owner_id = self.partner_id

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id.code in ['incoming']:
            self.owner_id = self.partner_id